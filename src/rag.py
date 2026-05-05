import os
import json
import networkx as nx
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from src.config import DATA_FILE, TRIPLES_FILE, CHROMA_DB_DIR

load_dotenv()

class EntityExtraction(BaseModel):
    entity: str = Field(description="The main entity mentioned in the question")

def get_flat_rag_chain():
    # Load document
    loader = TextLoader(DATA_FILE, encoding="utf-8")
    docs = loader.load()
    
    texts = [t.strip() for t in docs[0].page_content.split('\n') if t.strip()]
    
    # print(f"Indexing {len(texts)} sentences for Flat RAG...")
    
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=OpenAIEmbeddings(),
        collection_name="tech_corpus",
        persist_directory=CHROMA_DB_DIR
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    template = """You are an AI assistant. Answer the question based ONLY on the following context:
    {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])
        
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def load_graph():
    try:
        with open(TRIPLES_FILE, "r", encoding="utf-8") as f:
            triples = json.load(f)
    except FileNotFoundError:
        return nx.Graph()
        
    G = nx.Graph() # Use undirected graph for easier traversal
    for t in triples:
        G.add_edge(t["subject"], t["object"], label=t["relation"])
    return G

def get_subgraph_context(G, start_node, max_hops=2):
    target_node = None
    for n in G.nodes():
        if start_node.lower() in n.lower():
            target_node = n
            break
            
    if not target_node:
        return "No information found for this entity."
        
    # BFS up to max_hops
    visited = set()
    queue = [(target_node, 0)]
    context_triples = []
    
    while queue:
        current_node, depth = queue.pop(0)
        if current_node not in visited:
            visited.add(current_node)
            
            if depth < max_hops:
                for neighbor in G.neighbors(current_node):
                    if neighbor not in visited:
                        edge_data = G.get_edge_data(current_node, neighbor)
                        relation = edge_data.get('label', 'RELATED_TO')
                        context_triples.append(f"{current_node} - [{relation}] - {neighbor}")
                        queue.append((neighbor, depth + 1))
                        
    return "\n".join(context_triples)

def ask_graph_rag(question, G=None):
    if G is None:
        G = load_graph()
        
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # 1. Extract Entity
    structured_llm = llm.with_structured_output(EntityExtraction)
    entity_result = structured_llm.invoke(f"Extract the main company or person from this question: {question}")
    main_entity = entity_result.entity
    
    # 2. Get Context from Graph
    context = get_subgraph_context(G, main_entity, max_hops=2)
    
    # 3. Answer Question
    template = """You are an AI assistant. Answer the question based ONLY on the following context from a knowledge graph:
    {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = prompt | llm
    result = chain.invoke({"context": context, "question": question})
    return result.content, main_entity, context

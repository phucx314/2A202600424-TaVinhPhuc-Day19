import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def get_flat_rag_chain():
    # Load document
    loader = TextLoader("data.txt", encoding="utf-8")
    docs = loader.load()
    
    texts = [t.strip() for t in docs[0].page_content.split('\n') if t.strip()]
    
    print(f"Indexing {len(texts)} sentences for Flat RAG...")
    
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=OpenAIEmbeddings(),
        collection_name="tech_corpus"
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

if __name__ == "__main__":
    chain = get_flat_rag_chain()
    res = chain.invoke("Ai là CEO của công ty đã đầu tư vào OpenAI?")
    print("Test Flat RAG Answer:", res)

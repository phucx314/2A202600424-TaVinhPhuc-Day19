import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from src.config import DATA_FILE, TRIPLES_FILE

load_dotenv()

# Define the structure of a Triple
class Triple(BaseModel):
    subject: str = Field(description="The main entity (subject) of the relationship")
    relation: str = Field(description="The relationship between the subject and the object (e.g., FOUNDED_BY, CEO_OF, LOCATED_IN)")
    object: str = Field(description="The entity that is related to the subject")

class TriplesOutput(BaseModel):
    triples: List[Triple] = Field(description="List of extracted relationship triples")

def extract_triples():
    print(f"Reading {DATA_FILE}...")
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            corpus = f.read()
    except FileNotFoundError:
        print(f"File {DATA_FILE} not found. Please run the scraper first.")
        return
    
    sentences = [s.strip() for s in corpus.split(".") if s.strip()]
    print(f"Found {len(sentences)} sentences.")
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    structured_llm = llm.with_structured_output(TriplesOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at extracting information from text. "
                   "Your task is to extract entity-relationship triples from the given text. "
                   "The relationship should be a concise, capitalized string (like FOUNDED_BY, CEO_OF, LOCATED_IN, COMPETES_WITH, INVESTED_IN)."),
        ("user", "Extract triples from the following text:\n\n{text}")
    ])
    
    chain = prompt | structured_llm
    
    all_triples = []
    print("Extracting triples using LLM...")
    for idx, sentence in enumerate(sentences):
        print(f"Processing sentence {idx+1}/{len(sentences)}: {sentence}")
        try:
            result = chain.invoke({"text": sentence})
            for t in result.triples:
                all_triples.append({"subject": t.subject, "relation": t.relation, "object": t.object})
        except Exception as e:
            print(f"Error on sentence {idx+1}: {e}")
            
    print(f"Extracted a total of {len(all_triples)} triples.")
    
    with open(TRIPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(all_triples, f, ensure_ascii=False, indent=4)
    print(f"Saved to {TRIPLES_FILE}")

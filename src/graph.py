import json
import re
import networkx as nx
from pyvis.network import Network
from neo4j import GraphDatabase
from src.config import TRIPLES_FILE, GRAPH_HTML_FILE, NEO4J_URI, NEO4J_AUTH

def read_triples():
    try:
        with open(TRIPLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{TRIPLES_FILE} not found! Please run the extractor first.")
        return []

def build_networkx_graph():
    triples = read_triples()
    if not triples:
        return None
        
    print(f"Loaded {len(triples)} triples. Building Graph...")
    G = nx.DiGraph()
    
    for t in triples:
        subject = t["subject"]
        relation = t["relation"]
        obj = t["object"]
        G.add_edge(subject, obj, label=relation)
        
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

def create_interactive_graph():
    triples = read_triples()
    if not triples:
        return

    # Initialize PyVis network
    net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', directed=True)
    net.barnes_hut()

    print("Building Interactive Graph...")
    for t in triples:
        subject = t["subject"]
        relation = t["relation"]
        obj = t["object"]
        
        net.add_node(subject, label=subject, title=subject, color='#97c2fc')
        net.add_node(obj, label=obj, title=obj, color='#fb7e81')
        net.add_edge(subject, obj, title=relation, label=relation, color='gray')
        
    print(f"Graph generated with {len(net.nodes)} nodes and {len(net.edges)} edges.")
    
    # Save to HTML file
    net.save_graph(GRAPH_HTML_FILE)
    print(f"Graph saved to {GRAPH_HTML_FILE}. Open this file in your browser to view the interactive graph.")

def sanitize_relation(relation):
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', relation)
    clean = re.sub(r'_+', '_', clean)
    return clean.strip('_').upper()

def import_to_neo4j():
    triples = read_triples()
    if not triples:
        return

    print(f"Loaded {len(triples)} triples. Connecting to Neo4j...")
    
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
            print("Clearing old data in Neo4j...")
            driver.execute_query("MATCH (n) DETACH DELETE n", database_="neo4j")
            
            print("Importing new data...")
            for i, t in enumerate(triples):
                subject = t["subject"].strip()
                relation = sanitize_relation(t["relation"])
                obj = t["object"].strip()
                
                if not subject or not obj or not relation:
                    continue
                    
                cypher_query = f"""
                MERGE (s:Entity {{name: $subject}})
                MERGE (o:Entity {{name: $obj}})
                MERGE (s)-[r:{relation}]->(o)
                """
                
                driver.execute_query(
                    cypher_query,
                    subject=subject,
                    obj=obj,
                    database_="neo4j"
                )
                
                if (i + 1) % 50 == 0:
                    print(f" -> Imported {i + 1}/{len(triples)} triples...")
                    
        print("\n✅ HOÀN TẤT! Đã đẩy toàn bộ dữ liệu lên Neo4j.")
    except Exception as e:
        print(f"Lỗi kết nối tới Neo4j: {e}")

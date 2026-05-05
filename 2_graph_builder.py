import json
import networkx as nx

def build_knowledge_graph():
    print("Reading triples.json...")
    with open("triples.json", "r", encoding="utf-8") as f:
        triples = json.load(f)
        
    print(f"Loaded {len(triples)} triples. Building Graph...")
    G = nx.DiGraph()
    
    for t in triples:
        subject = t["subject"]
        relation = t["relation"]
        obj = t["object"]
        
        # Adding edges
        G.add_edge(subject, obj, label=relation)
        
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print("\n--- Graph Entities (Nodes) ---")
    print(G.nodes())
    
    print("\n--- Graph Relationships (Edges) ---")
    for u, v, d in G.edges(data=True):
        print(f"{u} -[{d['label']}]-> {v}")

if __name__ == "__main__":
    build_knowledge_graph()

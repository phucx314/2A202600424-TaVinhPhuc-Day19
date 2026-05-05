import json
from pyvis.network import Network

def create_interactive_graph():
    print("Reading triples.json...")
    with open("triples.json", "r", encoding="utf-8") as f:
        triples = json.load(f)

    # Initialize PyVis network
    net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', directed=True)
    
    # Optional: configure physics for better layout
    net.barnes_hut()

    print("Building Interactive Graph...")
    for t in triples:
        subject = t["subject"]
        relation = t["relation"]
        obj = t["object"]
        
        # Add nodes (PyVis handles duplicates automatically if same ID)
        net.add_node(subject, label=subject, title=subject, color='#97c2fc')
        net.add_node(obj, label=obj, title=obj, color='#fb7e81')
        
        # Add edge
        net.add_edge(subject, obj, title=relation, label=relation, color='gray')
        
    print(f"Graph generated with {len(net.nodes)} nodes and {len(net.edges)} edges.")
    
    # Save to HTML file
    net.save_graph("knowledge_graph.html")
    print("Graph saved to knowledge_graph.html. Open this file in your browser to view the interactive graph.")

if __name__ == "__main__":
    create_interactive_graph()

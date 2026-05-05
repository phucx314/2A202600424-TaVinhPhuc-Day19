import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# File paths
DATA_FILE = os.path.join(DATA_DIR, "data.txt")
TRIPLES_FILE = os.path.join(DATA_DIR, "triples.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.csv")
GRAPH_HTML_FILE = os.path.join(DATA_DIR, "knowledge_graph.html")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma")

# Neo4j Settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password123")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

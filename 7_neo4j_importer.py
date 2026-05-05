import json
import re
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

def sanitize_relation(relation):
    # Neo4j relationship types shouldn't have spaces or special characters
    # Convert "HAS DEGREE" to "HAS_DEGREE"
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', relation)
    # Remove multiple underscores
    clean = re.sub(r'_+', '_', clean)
    return clean.strip('_').upper()

def import_to_neo4j():
    print("Reading triples.json...")
    try:
        with open("triples.json", "r", encoding="utf-8") as f:
            triples = json.load(f)
    except FileNotFoundError:
        print("triples.json not found! Please run the extractor first.")
        return

    print(f"Loaded {len(triples)} triples. Connecting to Neo4j...")
    
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Xóa dữ liệu cũ để tránh trùng lặp nếu chạy nhiều lần
        print("Clearing old data in Neo4j...")
        driver.execute_query("MATCH (n) DETACH DELETE n", database_="neo4j")
        
        print("Importing new data...")
        for i, t in enumerate(triples):
            subject = t["subject"].strip()
            relation = sanitize_relation(t["relation"])
            obj = t["object"].strip()
            
            if not subject or not obj or not relation:
                continue
                
            # Tạo truy vấn Cypher động để có tên relationship động
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
    print("Mở trình duyệt: http://localhost:7474")
    print("Đăng nhập với neo4j / password123")
    print("Gõ truy vấn sau vào thanh lệnh của Neo4j Browser để xem đồ thị:")
    print("MATCH (n) RETURN n")

if __name__ == "__main__":
    import_to_neo4j()

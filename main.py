import argparse
import sys
from src.scraper import run_scraper
from src.extractor import extract_triples
from src.graph import build_networkx_graph, create_interactive_graph, import_to_neo4j
from src.evaluation import run_evaluation

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Pipeline Execution")
    parser.add_argument("--scrape", action="store_true", help="1. Scrape data from Wikipedia")
    parser.add_argument("--extract", action="store_true", help="2. Extract triples using LLM")
    parser.add_argument("--graph", action="store_true", help="3. Build graph (NetworkX) and visualize (PyVis)")
    parser.add_argument("--neo4j", action="store_true", help="4. Import triples to Neo4j")
    parser.add_argument("--evaluate", action="store_true", help="5. Run RAG evaluation")
    parser.add_argument("--all", action="store_true", help="Run the entire pipeline sequentially")
    
    args = parser.parse_args()
    
    # Nếu không truyền argument nào, mặc định in ra help
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nNote: You can run everything at once using --all")
        sys.exit(1)

    if args.all or args.scrape:
        print("\n" + "="*40)
        print("STEP 1: SCRAPING WIKIPEDIA DATA")
        print("="*40)
        run_scraper()
        
    if args.all or args.extract:
        print("\n" + "="*40)
        print("STEP 2: EXTRACTING TRIPLES")
        print("="*40)
        extract_triples()
        
    if args.all or args.graph:
        print("\n" + "="*40)
        print("STEP 3: BUILDING & VISUALIZING GRAPH")
        print("="*40)
        build_networkx_graph()
        create_interactive_graph()
        
    if args.all or args.neo4j:
        print("\n" + "="*40)
        print("STEP 4: PUSHING TO NEO4J")
        print("="*40)
        import_to_neo4j()
        
    if args.all or args.evaluate:
        print("\n" + "="*40)
        print("STEP 5: EVALUATION (FLAT RAG VS GRAPH RAG)")
        print("="*40)
        run_evaluation()

if __name__ == "__main__":
    main()

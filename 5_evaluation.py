import time
import csv
from importlib import import_module
from langchain_community.callbacks import get_openai_callback

flat_rag = import_module("3_flat_rag")
graph_rag = import_module("4_graph_rag")

def run_evaluation():
    questions = [
        "OpenAI được thành lập vào năm nào và bởi những ai?",
        "Microsoft đã đầu tư bao nhiêu tiền vào OpenAI trong năm 2019 và 2023?",
        "Google được thành lập bởi ai và vào thời gian nào?",
        "Ai đã thay thế Larry Page để trở thành CEO của Google?",
        "Microsoft thâu tóm LinkedIn vào năm nào và với giá bao nhiêu?",
        "Satya Nadella bắt đầu nhận vai trò CEO của Microsoft từ năm nào?",
        "Công ty nào được sáng lập bởi Bill Gates và Paul Allen?",
        "Apple được thành lập vào tháng 4 năm 1976 bởi những ai?",
        "Ai đã trở thành Giám đốc điều hành mới của Apple sau khi Steve Jobs từ chức vào tháng 8 năm 2011?",
        "Apple đã đạt được cột mốc định giá 2 nghìn tỷ đô la Mỹ vào thời gian nào?",
        "Anthropic được thành lập vào năm 2021 bởi những cựu thành viên của tổ chức nào?",
        "Ai là chủ tịch và CEO của Anthropic?",
        "Công ty xAI được thành lập bởi ai và vào năm nào?",
        "xAI là công ty con thuộc sở hữu của tập đoàn hàng không vũ trụ nào?",
        "Google DeepMind được thành lập ban đầu với tên gọi là gì?",
        "Chương trình AlphaGo của DeepMind đã làm được điều gì nổi bật vào năm 2016?",
        "Công ty nào đã mua lại DeepMind vào năm 2014?",
        "Sản phẩm chatbot AI nổi bật của xAI tên là gì?",
        "Các sản phẩm phần cứng mà Apple sản xuất bao gồm những gì?",
        "Microsoft đã tung ra máy tính bảng nào vào năm 2012?"
    ]
    
    print("Initializing Flat RAG...")
    flat_chain = flat_rag.get_flat_rag_chain()
    
    print("Loading Graph for GraphRAG...")
    G = graph_rag.load_graph()
    
    results = []
    
    for i, q in enumerate(questions):
        print(f"\n--- Question {i+1}: {q} ---")
        
        # Test Flat RAG
        with get_openai_callback() as cb_flat:
            start_time = time.time()
            flat_ans = flat_chain.invoke(q)
            flat_time = time.time() - start_time
            flat_tokens = cb_flat.total_tokens
        
        # Test Graph RAG
        with get_openai_callback() as cb_graph:
            start_time = time.time()
            graph_ans, entity, context = graph_rag.ask_graph_rag(q, G)
            graph_time = time.time() - start_time
            graph_tokens = cb_graph.total_tokens
        
        print(f"Flat RAG: {flat_ans} (Tokens: {flat_tokens}, Time: {flat_time:.2f}s)")
        print(f"Graph RAG: {graph_ans} (Tokens: {graph_tokens}, Time: {graph_time:.2f}s)")
        
        results.append({
            "Question": q,
            "Flat RAG Answer": flat_ans,
            "Flat RAG Tokens": flat_tokens,
            "Flat RAG Time (s)": round(flat_time, 2),
            "Graph RAG Answer": graph_ans,
            "Graph RAG Entity": entity,
            "Graph RAG Tokens": graph_tokens,
            "Graph RAG Time (s)": round(graph_time, 2)
        })
        
    with open("results.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Question", "Flat RAG Answer", "Flat RAG Tokens", "Flat RAG Time (s)", 
            "Graph RAG Answer", "Graph RAG Entity", "Graph RAG Tokens", "Graph RAG Time (s)"
        ])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print("\nSaved evaluation results to results.csv")
    
if __name__ == "__main__":
    run_evaluation()

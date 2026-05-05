import requests
import re
import os

def scrape_wikipedia(company_name, lang="vi"):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "titles": company_name,
        "format": "json",
        "explaintext": True,
    }
    
    headers = {
        "User-Agent": "GraphRAGLabBot/1.0 (student@example.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        pages = data["query"]["pages"]
        for page_id, page_info in pages.items():
            if page_id == "-1":
                print(f" [!] Không tìm thấy Wikipedia cho: {company_name} (lang: {lang})")
                return ""
            return page_info.get("extract", "")
    except Exception as e:
        print(f" [!] Lỗi khi cào dữ liệu {company_name}: {e}")
        return ""

def main():
    # Danh sách các công ty cần cào dữ liệu và ngôn ngữ ưu tiên
    # Dùng tiếng Anh (en) cho các công ty mới vì wiki tiếng Việt có thể chưa cập nhật
    companies = {
        "OpenAI": "vi",
        "Google": "vi",
        "Microsoft": "vi",
        "Apple Inc.": "vi",
        "Anthropic": "en",
        "XAI (company)": "en",
        "DeepMind": "vi"
    }
    
    all_text = []
    
    print("=== BẮT ĐẦU CÀO DỮ LIỆU TỪ WIKIPEDIA ===")
    for company, lang in companies.items():
        print(f"Đang lấy thông tin: {company}...")
        text = scrape_wikipedia(company, lang)
        
        if text:
            # Xóa các khoảng trắng thừa, dòng rỗng
            cleaned_text = re.sub(r'\n+', '\n', text).strip()
            
            # Tách thành từng câu (dựa trên dấu chấm) để mỗi dòng là 1 câu
            # Việc này giúp LLM (ở file 1_extractor.py) dễ dàng trích xuất Triples hơn
            sentences = [s.strip() + "." for s in cleaned_text.split(".") if len(s.strip()) > 10]
            
            all_text.extend(sentences)
            print(f" -> Đã lấy được {len(sentences)} câu.")
            
    final_corpus = "\n".join(all_text)
    
    # Ghi đè vào data.txt
    with open("data.txt", "w", encoding="utf-8") as f:
        f.write(final_corpus)
        
    print(f"\n=== HOÀN TẤT! Đã lưu {len(all_text)} câu vào data.txt ===")
    print("Bây giờ bạn có thể chạy lại script ./run.sh để hệ thống tự động:")
    print("1. Đọc file data.txt mới")
    print("2. Trích xuất lại Triples mới (tốn token)")
    print("3. Vẽ lại Graph mới")
    print("4. Chạy lại Evaluation")

if __name__ == "__main__":
    main()

# GraphRAG Pipeline: Tech Company Corpus

Dự án này là bài Lab 19 nhằm xây dựng một hệ thống GraphRAG hoàn chỉnh từ đầu đến cuối (End-to-End). Hệ thống tự động thu thập thông tin các công ty công nghệ lớn (Tech Company Corpus) từ Wikipedia, trích xuất các mối quan hệ thực thể (Triples) bằng LLM, xây dựng đồ thị tri thức (Knowledge Graph) và đánh giá hiệu năng truy vấn so với hệ thống Flat RAG truyền thống.

## 1. Cấu trúc Dự án

Dự án được thiết kế theo cấu trúc module để dễ bảo trì và mở rộng:

```text
day019/
├── src/                      
│   ├── config.py             # Cấu hình đường dẫn và Database
│   ├── scraper.py            # Script cào dữ liệu từ Wikipedia (OpenAI, Google, Apple...)
│   ├── extractor.py          # Trích xuất Triples bằng LangChain & OpenAI
│   ├── graph.py              # Xây dựng NetworkX, PyVis và đẩy dữ liệu lên Neo4j
│   ├── rag.py                # Pipeline xử lý cho Flat RAG (Chroma) và Graph RAG (BFS)
│   └── evaluation.py         # Script chạy benchmark 20 câu hỏi đánh giá
├── data/                     
│   ├── data.txt              # Văn bản thô thu thập được
│   ├── triples.json          # File chứa danh sách các bộ ba (Subject - Relation - Object)
│   ├── results.csv           # Bảng kết quả Evaluation
│   ├── knowledge_graph.html  # File HTML tương tác của đồ thị
│   └── chroma/               # Vector Database cục bộ
├── extras/
│   └── lite version.png      # Ảnh chụp đồ thị Neo4j
├── main.py                   # Bảng điều khiển trung tâm (Orchestrator)
└── run.sh                    # Script khởi chạy tự động
```

## 2. Cách thức hoạt động & Cài đặt

Bạn có thể chạy toàn bộ pipeline tự động từ đầu đến cuối bằng lệnh:
```bash
bash run.sh
```

Hoặc chạy từng bước độc lập thông qua `main.py`:
- `python main.py --scrape`: Cào dữ liệu văn bản thô
- `python main.py --extract`: Dùng LLM trích xuất Triples
- `python main.py --graph`: Vẽ đồ thị (NetworkX & PyVis)
- `python main.py --neo4j`: Đẩy dữ liệu vào Neo4j DB
- `python main.py --evaluate`: Chạy benchmark

## 3. Trực quan hóa Knowledge Graph (Neo4j)

Dưới đây là hình ảnh đồ thị tri thức được tạo ra sau khi hệ thống phân tích bộ dữ liệu Wikipedia:

![Knowledge Graph Visualization](extras/lite%20version.png)

## 4. Kết quả Đánh giá (Evaluation: Flat RAG vs Graph RAG)

Chúng tôi đã tiến hành benchmark trên 20 câu hỏi thực tế. Dưới đây là phân tích tóm tắt:

### a) Khả năng tránh Ảo giác (Hallucination)
Flat RAG (dùng tìm kiếm Vector thông thường) bị lỗi ảo giác rất nặng ở những câu hỏi mang tính suy luận hoặc khi các thực thể nằm rải rác:
- **Câu hỏi:** *Ai là chủ tịch và CEO của Anthropic?*
  - **Flat RAG:** Trả lời sai (*"Elon Musk là chủ tịch và CEO của Anthropic."*) do lẫn lộn ngữ cảnh.
  - **Graph RAG:** Trả lời chính xác (*"Dario Amodei là chủ tịch..."*) nhờ duyệt đồ thị 2-hop đúng hướng.
- **Câu hỏi:** *Sản phẩm chatbot AI nổi bật của xAI tên là gì?*
  - **Flat RAG:** Trả lời sai hoàn toàn sang OpenAI (*"Sản phẩm chatbot AI nổi bật của OpenAI là GPT-3."*).
  - **Graph RAG:** Trả lời chính xác (*"Grok"*).
- **Câu hỏi:** *xAI là công ty con thuộc sở hữu của tập đoàn hàng không vũ trụ nào?*
  - **Flat RAG:** Bịa ra thông tin (*"OpenAI LP"*).
  - **Graph RAG:** Nhận diện đúng mối liên hệ (*"SpaceX"*).

### b) Phân tích Chi phí (Token & Time)
Dựa vào dữ liệu từ `results.csv`:
- **Flat RAG:** Tốc độ phản hồi cực nhanh (trung bình **~1.5s**) và tiêu tốn ít token (khoảng **~200 - 300 tokens** mỗi truy vấn) do chỉ cần lấy top-k đoạn văn bản.
- **Graph RAG:** Tốn nhiều token hơn (trung bình **~400 - 1200 tokens**) và thời gian xử lý chậm hơn một chút (**~1.8s - 2.5s**) do phải trải qua bước: (1) Nhận diện thực thể bằng LLM, (2) Lấy các mối quan hệ (Edges) liên quan từ đồ thị, và (3) Tổng hợp câu trả lời.

**Kết luận:** Graph RAG tốn kém tài nguyên hơn trong quá trình truy vấn, nhưng mang lại độ chính xác gần như tuyệt đối, đặc biệt là với cấu trúc dữ liệu nhiều chiều và chồng chéo (như các công ty công nghệ có chung nhà đầu tư hoặc lịch sử thâu tóm).

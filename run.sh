#!/bin/bash

# Kích hoạt môi trường ảo (venv) đã có sẵn từ Lab 17 (chứa chromadb, langchain, networkx...)
source "../day017/lab17/venv/bin/activate"

echo "=== 1. Extracting Triples ==="
python 0_scraper.py
python 1_extractor.py

echo "=== 2. Building Graph ==="
python 2_graph_builder.py
python 6_visualize.py

echo "=== 3. Testing Flat RAG ==="
python 3_flat_rag.py

echo "=== 4. Testing Graph RAG ==="
python 4_graph_rag.py

echo "=== 5. Running Evaluation ==="
python 5_evaluation.py

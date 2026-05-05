#!/bin/bash

# Kích hoạt môi trường ảo (venv) đã có sẵn từ Lab 17
source "../day017/lab17/venv/bin/activate"

# Thêm PYTHONPATH để Python hiểu cấu trúc thư mục src/
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Starting GraphRAG Pipeline..."
python main.py --all

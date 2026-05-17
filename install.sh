#!/bin/bash
set -e

echo "=== Mad Professor 安裝腳本 ==="
echo ""

# 1. faiss-cpu
echo "[1/6] 安裝 faiss-cpu..."
pip install faiss-cpu

# 2. langchain 相關
echo "[2/6] 安裝 langchain..."
pip install langchain langchain-community langchain-text-splitters

# 3. google-genai
echo "[3/6] 安裝 google-genai..."
pip install google-genai

# 4. fastapi + uvicorn
echo "[4/6] 安裝 fastapi + uvicorn..."
pip install fastapi uvicorn python-multipart

# 5. 工具套件
echo "[5/6] 安裝工具套件..."
pip install python-dotenv pydantic-settings requests numpy

# 6. PyMuPDF
echo "[6/6] 安裝 PyMuPDF..."
pip install pymupdf

echo ""
echo "=== 安裝完成 ==="
echo ""
echo "驗證："
python3 -c "
import fastapi; print('fastapi:', fastapi.__version__)
import uvicorn; print('uvicorn:', uvicorn.__version__)
import google.genai; print('google-genai: ok')
import langchain; print('langchain:', langchain.__version__)
import faiss; print('faiss: ok')
import fitz; print('PyMuPDF:', fitz.__version__)
import numpy; print('numpy:', numpy.__version__)
import dotenv; print('python-dotenv: ok')
print('✅ 全部通過')
"

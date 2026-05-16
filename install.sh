#!/bin/bash
set -e

echo "=== Mad Professor 安裝腳本 ==="
echo ""

# 1. torch CPU 版（明確指定，避免裝到 CUDA 版）
echo "[1/9] 安裝 torch (CPU)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 2. sentence-transformers（Embedding 模型）
echo "[2/9] 安裝 sentence-transformers..."
pip install sentence-transformers --no-deps
pip install transformers tokenizers huggingface-hub tqdm scikit-learn scipy

# 3. faiss-cpu（向量庫）
echo "[3/9] 安裝 faiss-cpu..."
pip install faiss-cpu --no-deps
pip install numpy packaging

# 4. langchain 相關
echo "[4/9] 安裝 langchain..."
pip install langchain langchain-community langchain-huggingface langchain-text-splitters

# 5. google-genai
echo "[5/9] 安裝 google-genai..."
pip install google-genai

# 6. fastapi + uvicorn
echo "[6/9] 安裝 fastapi + uvicorn..."
pip install fastapi uvicorn python-multipart

# 7. python-dotenv
echo "[7/9] 安裝 python-dotenv..."
pip install python-dotenv

# 8. requests
echo "[8/9] 安裝 requests..."
pip install requests

# 9. zhconv（繁簡轉換）
echo "[9/9] 安裝 zhconv..."
pip install zhconv

echo ""
echo "=== 安裝完成 ==="
echo ""
echo "驗證："
python3 -c "
import torch; print('torch:', torch.__version__, '| CUDA:', torch.cuda.is_available())
import fastapi; print('fastapi:', fastapi.__version__)
import uvicorn; print('uvicorn:', uvicorn.__version__)
import google.genai; print('google-genai: ok')
import langchain; print('langchain:', langchain.__version__)
import sentence_transformers; print('sentence_transformers:', sentence_transformers.__version__)
import faiss; print('faiss: ok')
import dotenv; print('python-dotenv: ok')
import zhconv; print('zhconv: ok')
print('✅ 全部通過')
"

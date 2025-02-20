# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# コンテナ起動時のコマンド
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
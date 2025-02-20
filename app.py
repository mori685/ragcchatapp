import streamlit as st
from pathlib import Path
import json

# Streamlitのページ設定
st.set_page_config(
    page_title="RAG Chat App",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .stApp {
        max-width: 1980px !important;
        margin: 0 auto;
    }
    .main .block-container {
        max-width: 1980px !important;
        padding-left: 5rem;
        padding-right: 5rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# メインページの内容
st.title("🏠 RAG Chat Application")
st.markdown("""
## Welcome to RAG Chat Application

このアプリケーションでは、以下の機能を提供します：

1. **📄 Document Upload**
   - 複数の文書をアップロードし、管理できます
   - サポートされているファイル形式: TXT, PDF, CSV, XLSX, DOCX

2. **💬 Chat Interface**
   - アップロードした文書に基づいて質問ができます
   - 文書ごとに独立した会話を管理します
   - ソース情報を確認できます
            
3. **💬 今後の発展**    
   - スケーラビリティ
    - 大量の文書を効率的に管理・検索できる
    - ベクトルDBを用いることで、高速な検索と更新が可能
    - 文書の追加・更新・削除を動的に行える
    - 複数のユーザーが同時にアクセスできる
            
   - コスト効率
    - ChatGPTやClaudeの標準機能は文書の制限があり、大量の文書を扱う場合は非効率
    - APIを使用することで、必要な機能のみを利用でき、コストを最適化できる
    - 自社のインフラ上で動作させることで、長期的なコストを抑制できる
            

### 使い方

1. 左サイドバーの "Document Upload" ページで文書をアップロードします
2. "Chat Interface" ページで特定の文書を選択し、質問を開始します
3. 各文書について独立した会話を行うことができます

### 注意事項

- アップロードされた文書は一時的に保存され、セッション終了時に削除されます
- 会話の履歴はブラウザのセッション内で保持されます
""")

# セッション状態の初期化
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = {}

if 'current_doc' not in st.session_state:
    st.session_state.current_doc = None
import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import (
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    Docx2txtLoader
)
from langchain.document_loaders.pdf import PyPDFLoader as PDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os
from dotenv import load_dotenv
import tempfile
import json

# 環境変数の読み込み
load_dotenv()

# Streamlitのページ設定
st.set_page_config(
    page_title="Document Upload",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = {}

def get_loader_for_filetype(file_path, file_type):
    """ファイルタイプに応じた適切なローダーを返す"""
    loaders = {
        'txt': TextLoader,
        'pdf': PDFLoader,
        'csv': CSVLoader,
        'xlsx': UnstructuredExcelLoader,
        'docx': Docx2txtLoader
    }
    return loaders.get(file_type.lower(), TextLoader)(file_path)

def process_document(uploaded_file):
    """アップロードされたドキュメントを処理する"""
    try:
        file_type = uploaded_file.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        # ドキュメントの読み込みと分割
        loader = get_loader_for_filetype(file_path, file_type)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separator="\n"
        )
        splits = text_splitter.split_documents(documents)

        # Vectorストアの作成
        embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        vectorstore = Chroma.from_documents(splits, embeddings)
        
        # ドキュメント情報を保存
        st.session_state.processed_docs[uploaded_file.name] = {
            'vectorstore': vectorstore,
            'messages': [],
            'summary': documents[0].page_content[:200] + "..."  # 簡単な要約として最初の200文字を使用
        }

        # 一時ファイルの削除
        os.unlink(file_path)
        return True

    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False

# メインエリア
st.title("📄 Document Upload")

# ファイルアップロード
uploaded_files = st.file_uploader(
    "Upload documents",
    type=['txt', 'pdf', 'csv', 'xlsx', 'docx'],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.processed_docs:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                if process_document(uploaded_file):
                    st.success(f"Successfully processed {uploaded_file.name}")

# 処理済みドキュメント一覧
if st.session_state.processed_docs:
    st.subheader("📚 Processed Documents")
    for doc_name, doc_info in st.session_state.processed_docs.items():
        with st.expander(f"📄 {doc_name}"):
            st.write("Preview:")
            st.text(doc_info['summary'])
            if st.button(f"Remove {doc_name}", key=f"remove_{doc_name}"):
                del st.session_state.processed_docs[doc_name]
                st.experimental_rerun()

else:
    st.info("👆 Start by uploading documents. Supported formats: TXT, PDF, CSV, XLSX, DOCX")

# 使用方法の説明
st.markdown("""
### 使用方法

1. 上部のファイルアップローダーを使用して文書をアップロード
2. 処理が完了するまで待機
3. アップロードされた文書は自動的に処理され、チャット用に準備されます
4. "Chat Interface" ページで文書を選択し、質問を開始できます

### 注意事項

- 大きなファイルの処理には時間がかかる場合があります
- アップロードされた文書は一時的に保存され、セッション終了時に削除されます
""")
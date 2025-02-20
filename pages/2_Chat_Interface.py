import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Streamlitのページ設定
st.set_page_config(
    page_title="Chat Interface",
    page_icon="💬",
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
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        min-height: 1080px;
    }
</style>
""", unsafe_allow_html=True)

# 文書が処理されていない場合の処理
if 'processed_docs' not in st.session_state or not st.session_state.processed_docs:
    st.error("😅 No documents found. Please upload documents in the Document Upload page first!")
    st.stop()

# サイドバーでドキュメント選択
with st.sidebar:
    st.header("💬 Chat Settings")
    
    # ドキュメント選択
    selected_doc = st.selectbox(
        "Select Document",
        options=list(st.session_state.processed_docs.keys()),
        key="document_selector"
    )
    
    # 会話チェーンの作成（ドキュメントが選択されている場合）
    if selected_doc:
        if 'conversation_chains' not in st.session_state:
            st.session_state.conversation_chains = {}
        
        if selected_doc not in st.session_state.conversation_chains:
            st.session_state.conversation_chains[selected_doc] = ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(
                    temperature=st.session_state.get('temperature', 0.7),
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                ),
                retriever=st.session_state.processed_docs[selected_doc]['vectorstore'].as_retriever(
                    search_kwargs={"k": 3}
                ),
                verbose=True
            )
    
    # 設定
    st.subheader("⚙️ Settings")
    temperature = st.slider(
        "AI Response Creativity",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get('temperature', 0.7),
        step=0.1
    )
    st.session_state.temperature = temperature
    
    # 現在の会話をクリア
    if st.button("🗑️ Clear Current Chat"):
        if selected_doc in st.session_state.processed_docs:
            st.session_state.processed_docs[selected_doc]['messages'] = []
            st.experimental_rerun()

# メインエリア
st.title(f"💬 Chat with: {selected_doc}")

# 選択された文書のプレビュー
with st.expander("📄 Document Preview"):
    st.write(st.session_state.processed_docs[selected_doc]['summary'])

# チャット履歴の表示
messages = st.session_state.processed_docs[selected_doc]['messages']
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("Ask me anything about the document..."):
    # チャット履歴の準備
    chat_history = [(msg["role"], msg["content"]) for msg in messages]
    
    # ユーザーメッセージの表示と保存
    st.session_state.processed_docs[selected_doc]['messages'].append({
        "role": "user", 
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # アシスタントの応答
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 会話チェーンを使用して応答を生成
            result = st.session_state.conversation_chains[selected_doc]({
                "question": prompt,
                "chat_history": chat_history
            })
            
            answer = result["answer"]
            
            # 応答の表示
            st.markdown(answer)
            
            # 応答の保存
            st.session_state.processed_docs[selected_doc]['messages'].append({
                "role": "assistant",
                "content": answer
            })

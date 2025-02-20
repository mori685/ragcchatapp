import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Streamlitのページ設定
st.set_page_config(
    page_title="General Chat",
    page_icon="🤖",
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
    .user-message {
        background-color: #f0f2f6;
    }
    .assistant-message {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "general_messages" not in st.session_state:
    st.session_state.general_messages = []
if "chat_model" not in st.session_state:
    st.session_state.chat_model = ChatOpenAI(
        model_name="gpt-4-turbo-preview",  # 最新のGPT-4モデルを使用
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

# サイドバー設定
with st.sidebar:
    st.header("🤖 Chat Settings")
    
    # モデル選択
    model_name = st.selectbox(
        "Select Model",
        ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
        index=0
    )
    
    # 温度設定
    temperature = st.slider(
        "Response Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    # モデルまたは温度が変更された場合、新しいモデルインスタンスを作成
    if (model_name != st.session_state.chat_model.model_name or 
        temperature != st.session_state.chat_model.temperature):
        st.session_state.chat_model = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    # チャット履歴のクリア
    if st.button("🗑️ Clear Chat History"):
        st.session_state.general_messages = []
        st.experimental_rerun()

# メインエリア
st.title("🤖 Advanced AI Chat")

# モデル情報の表示
st.markdown(f"""
<div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
    <strong>Current Model:</strong> {model_name}<br>
    <strong>Temperature:</strong> {temperature}
</div>
""", unsafe_allow_html=True)

# チャット履歴の表示
for message in st.session_state.general_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("Send a message..."):
    # ユーザーメッセージの表示と保存
    st.session_state.general_messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # メッセージ履歴の作成
    messages = [
        HumanMessage(content=msg["content"]) if msg["role"] == "user"
        else AIMessage(content=msg["content"])
        for msg in st.session_state.general_messages
    ]
    
    # アシスタントの応答
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_model.predict_messages(messages)
            st.markdown(response.content)
            
            # 応答の保存
            st.session_state.general_messages.append({
                "role": "assistant",
                "content": response.content
            })

# 初期説明
if not st.session_state.general_messages:
    st.info("""
    👋 Welcome to the Advanced AI Chat!
    
    This chat uses the latest GPT-4 model for maximum accuracy and capability.
    You can:
    - Ask complex questions
    - Get detailed explanations
    - Solve challenging problems
    - Engage in sophisticated discussions
    
    Customize the settings in the sidebar to suit your needs:
    - Choose between different AI models
    - Adjust the response creativity
    
    Start chatting by typing your message below!
    """)

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="First Step",
    page_icon="💬",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #142b55 0%, #080d1b 42%, #05070d 100%);
        color: #f4f7ff;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(120, 160, 255, 0.15);
        border-radius: 16px;
        padding: 12px;
        background: rgba(18, 29, 54, 0.55);
    }
    [data-testid="stChatInput"] {
        border-color: rgba(95, 145, 255, 0.45);
    }
    h1 {
        letter-spacing: -1px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("First Step")
st.caption("A small step towards smarter conversations.")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "OpenRouter API key",
        value=os.getenv("OPENROUTER_API_KEY", ""),
        type="password",
        help="Your key is used only for requests from this app. Do not share it.",
    )
    model = st.text_input(
        "Model",
        value=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        help="You can keep openrouter/free or enter another model ID available on OpenRouter.",
    )
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Message First Step...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.warning("Add your OpenRouter API key in the sidebar to start chatting.")
    else:
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "First Step",
                },
            )

            api_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are First Step, a helpful, friendly, clear AI assistant. "
                        "Give practical answers and explain technical steps simply."
                    ),
                }
            ]
            api_messages.extend(st.session_state.messages)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model=model.strip() or "openrouter/free",
                        messages=api_messages,
                        temperature=temperature,
                    )
                    answer = response.choices[0].message.content or "I couldn't generate a response."
                st.markdown(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as error:
            st.error(f"Something went wrong: {error}")
            st.info(
                "Check that your OpenRouter key is valid, your model ID is available, "
                "and your internet connection is working."
            )

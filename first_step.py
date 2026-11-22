import os
import re
import base64
import mimetypes
from io import BytesIO
from collections import Counter

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from docx import Document

load_dotenv()

st.set_page_config(
    page_title="First Step",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp {
        background:
            radial-gradient(ellipse at 12% 0%, rgba(37, 99, 235, 0.22), transparent 38%),
            radial-gradient(ellipse at 88% 12%, rgba(29, 78, 216, 0.10), transparent 32%),
            #070B14;
        color: #E8EEFF;
    }
    [data-testid="stHeader"] { background: rgba(7, 11, 20, 0.75); }
    [data-testid="stToolbar"] { right: 1rem; }
    .block-container { max-width: 900px; padding-top: 2.2rem; padding-bottom: 7rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1628 0%, #090F1D 100%);
        border-right: 1px solid rgba(125, 160, 255, 0.12);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    .brand-row { display:flex; align-items:center; gap:12px; margin-bottom:1.7rem; }
    .brand-icon {
        width:42px; height:42px; display:flex; align-items:center; justify-content:center;
        border-radius:13px; color:white; font-size:21px;
        background:linear-gradient(135deg,#3B82F6,#1D4ED8);
    }
    .brand-name { color:#F4F7FF; font-size:1.2rem; font-weight:750; letter-spacing:-.5px; line-height:1.2; }
    .brand-caption { color:#8292B3; font-size:.76rem; margin-top:3px; }
    .hero { text-align:center; padding:2.5rem 1rem 1.6rem; margin:0 auto 1.3rem; }
    .hero-pill {
        display:inline-block; padding:6px 12px; margin-bottom:1rem;
        border:1px solid rgba(96,165,250,.28); border-radius:999px;
        color:#93C5FD; background:rgba(37,99,235,.10); font-size:.76rem;
    }
    .hero h1 { color:#F8FAFF; font-size:clamp(2.2rem,6vw,3.4rem); font-weight:800; letter-spacing:-2px; line-height:1.08; margin:0 0 .8rem; }
    .hero h1 span { color:#60A5FA; }
    .hero p { color:#9AAAC7; font-size:1rem; line-height:1.6; margin:0 auto; max-width:510px; }
    .suggestion-card {
        height:100%; min-height:112px; padding:16px;
        border:1px solid rgba(125,160,255,.14); border-radius:15px;
        background:linear-gradient(145deg,rgba(19,34,61,.88),rgba(12,21,39,.78));
    }
    .suggestion-icon { font-size:1.15rem; margin-bottom:8px; }
    .suggestion-title { color:#E8EEFF; font-size:.9rem; font-weight:650; margin-bottom:4px; }
    .suggestion-copy { color:#8FA0BF; font-size:.78rem; line-height:1.45; }
    [data-testid="stChatMessage"] {
        border:1px solid rgba(125,160,255,.13); border-radius:18px; padding:14px 16px;
        background:rgba(15,25,45,.78); margin-bottom:12px;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background:rgba(24,53,102,.48); border-color:rgba(59,130,246,.22);
    }
    [data-testid="stChatInput"] {
        border:1px solid rgba(96,165,250,.35); border-radius:17px;
        background:rgba(12,20,36,.96);
    }
    [data-testid="stChatInput"]:focus-within { border-color:rgba(96,165,250,.75); }
    .stButton > button {
        border-radius:11px; border:1px solid rgba(96,165,250,.22);
        background:rgba(37,99,235,.12); color:#DCEBFF;
    }
    .stButton > button:hover { border-color:rgba(96,165,250,.65); background:rgba(37,99,235,.22); color:white; }
    [data-testid="stSidebar"] .stButton > button { width:100%; }
    h2,h3 { color:#EDF3FF; letter-spacing:-.4px; }
    .sidebar-note { color:#7587A8; font-size:.75rem; line-height:1.5; margin-top:1rem; }
    .footer-note { color:#64748B; font-size:.75rem; text-align:center; padding-top:1rem; }
    @media (max-width:640px) {
        .block-container { padding-top:1.2rem; }
        .hero { padding-top:1.6rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- API configuration ----------
def get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


api_key = get_secret("OPENROUTER_API_KEY")
default_model = get_secret("OPENROUTER_MODEL", "openrouter/free")
default_vision_model = get_secret("OPENROUTER_VISION_MODEL", "google/gemini-2.5-flash")

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    st.session_state.documents = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False


# ---------- Document helpers ----------
def extract_document(uploaded_file):
    """Extract readable text from supported document formats."""
    data = uploaded_file.getvalue()
    name = uploaded_file.name
    extension = name.rsplit(".", 1)[-1].lower()

    if extension == "pdf":
        reader = PdfReader(BytesIO(data))
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"[Page {page_number}]\n{page_text}")
        return "\n\n".join(pages)

    if extension == "docx":
        document = Document(BytesIO(data))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(paragraphs)

    if extension == "txt":
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")

    raise ValueError("Unsupported document type.")


def split_into_chunks(text, chunk_size=1200, overlap=180):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def retrieve_relevant_chunks(question, limit=4):
    """Simple local keyword retrieval; no external embedding service is required."""
    terms = set(re.findall(r"[a-zA-Z0-9]{2,}", question.lower()))
    if not terms:
        return []

    ranked = []
    for item in st.session_state.documents:
        words = re.findall(r"[a-zA-Z0-9]{2,}", item["text"].lower())
        counts = Counter(words)
        score = sum(counts[t] for t in terms)
        if score:
            ranked.append((score, item))

    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in ranked[:limit]]


def make_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://first-step.streamlit.app",
            "X-Title": "First Step",
        },
    )


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-icon">✦</div>
            <div>
                <div class="brand-name">First Step</div>
                <div class="brand-caption">Your 1st step towards smarter conversations.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋  New chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.rerun()

    st.divider()
    st.subheader("Preferences")
    model = st.text_input("AI model", value=default_model, help="Enter a text-capable model ID available on OpenRouter.")
    vision_model = st.text_input(
        "Vision model",
        value=default_vision_model,
        help="Choose an OpenRouter model that supports image inputs.",
    )
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    st.divider()
    st.caption(f"{len(st.session_state.messages) // 2} messages in this chat")
    st.caption(f"{len(st.session_state.documents)} document chunks available")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_started = False
        st.rerun()

    if st.button("Remove uploaded documents", use_container_width=True):
        st.session_state.documents = []
        st.rerun()

    st.markdown(
        """
        <div class="sidebar-note">
            Your API key is loaded from Streamlit Secrets and is not displayed here.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Main screen ----------
if not st.session_state.messages:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-pill">FIRST STEP</div>
            <h1>Your next idea<br>starts <span>here.</span></h1>
            <p>Ask questions, explore ideas, learn something new, or start with an image or document.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="suggestion-card"><div class="suggestion-icon">💡</div><div class="suggestion-title">Explore an idea</div><div class="suggestion-copy">Turn a random thought into something meaningful.</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="suggestion-card"><div class="suggestion-icon">📚</div><div class="suggestion-title">Learn something</div><div class="suggestion-copy">Break down complex topics into simple explanations.</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="suggestion-card"><div class="suggestion-icon">📎</div><div class="suggestion-title">Read your files</div><div class="suggestion-copy">Ask questions about images, notes and documents.</div></div>', unsafe_allow_html=True)
else:
    st.markdown("### Your conversation")
    st.caption("Keep exploring. Every good idea starts somewhere.")


# ---------- Render conversation ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message.get("display", ""))
            for image_data in message.get("images", []):
                st.image(image_data, width=220)
        else:
            st.markdown(message["content"])


# ---------- Upload controls ----------
st.markdown("#### Attach files")
image_files = st.file_uploader(
    "Images (JPG, JPEG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    key="image_uploads",
)
document_files = st.file_uploader(
    "Documents (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="document_uploads",
    help="Uploaded documents are processed locally in this app session for question answering.",
)

if document_files:
    existing_names = {item["filename"] for item in st.session_state.documents}
    added_count = 0
    for uploaded in document_files:
        if uploaded.name in existing_names:
            continue
        try:
            extracted = extract_document(uploaded)
            chunks = split_into_chunks(extracted)
            for index, chunk in enumerate(chunks, start=1):
                st.session_state.documents.append(
                    {"filename": uploaded.name, "chunk": index, "text": chunk}
                )
            existing_names.add(uploaded.name)
            added_count += 1
            if not chunks:
                st.warning(f"No selectable text was found in {uploaded.name}. Scanned PDFs need OCR, which is not included yet.")
        except Exception as error:
            st.error(f"Could not read {uploaded.name}: {error}")
    if added_count:
        st.success(f"Added {added_count} document(s). You can now ask questions about their contents.")


# ---------- Chat input and response ----------
prompt = st.chat_input("Message First Step...")

if prompt:
    st.session_state.chat_started = True

    image_payloads = []
    image_data_for_display = []
    for uploaded_image in (image_files or []):
        raw = uploaded_image.getvalue()
        if len(raw) > 10 * 1024 * 1024:
            st.warning(f"{uploaded_image.name} is over 10 MB and was skipped.")
            continue
        mime_type = uploaded_image.type or mimetypes.guess_type(uploaded_image.name)[0] or "image/jpeg"
        encoded = base64.b64encode(raw).decode("utf-8")
        data_url = f"data:{mime_type};base64,{encoded}"
        image_payloads.append({"type": "image_url", "image_url": {"url": data_url}})
        image_data_for_display.append(raw)

    relevant_chunks = retrieve_relevant_chunks(prompt)
    document_context = ""
    if relevant_chunks:
        context_parts = []
        for item in relevant_chunks:
            context_parts.append(
                f"Source: {item['filename']} (chunk {item['chunk']})\n{item['text']}"
            )
        document_context = (
            "\n\nUse the following retrieved document excerpts to answer the user's question. "
            "Base document-specific claims on these excerpts. If the excerpts do not contain "
            "the answer, say so clearly.\n\n"
            + "\n\n---\n\n".join(context_parts)
        )

    api_user_text = prompt + document_context
    if image_payloads:
        api_user_content = [{"type": "text", "text": api_user_text or "Please examine the attached image(s)."}] + image_payloads
    else:
        api_user_content = api_user_text

    st.session_state.messages.append(
        {
            "role": "user",
            "content": api_user_content,
            "display": prompt,
            "images": image_data_for_display,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)
        for image_data in image_data_for_display:
            st.image(image_data, width=220)

    if not api_key:
        st.error("The OpenRouter API key is missing. Add OPENROUTER_API_KEY in your Streamlit app Secrets.")
    else:
        try:
            client = make_client()
            has_images = bool(image_payloads)
            selected_model = (vision_model if has_images else model).strip()
            selected_model = selected_model or (default_vision_model if has_images else default_model)

            api_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are First Step, a helpful, friendly, clear AI assistant. "
                        "Give practical answers and explain technical steps simply. "
                        "When a user provides an image, inspect its visible contents carefully. "
                        "Do not claim to read details that are not legible."
                    ),
                }
            ]
            for item in st.session_state.messages:
                api_messages.append({"role": item["role"], "content": item["content"]})

            with st.chat_message("assistant"):
                with st.spinner("First Step is thinking..."):
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=api_messages,
                        temperature=temperature,
                        max_tokens=4096,
                    )
                    answer = response.choices[0].message.content or "I couldn't generate a response. Please try again."
                st.markdown(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as error:
            st.error(f"Something went wrong: {error}")
            st.info(
                "If you attached an image, check that the selected vision model supports image inputs. "
                "Also verify that the model ID is available on OpenRouter and your API key is valid."
            )

st.markdown(
    '<div class="footer-note">First Step · Your 1st step towards smarter conversations.</div>',
    unsafe_allow_html=True,
)

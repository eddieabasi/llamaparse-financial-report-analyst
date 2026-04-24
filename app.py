import os
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from ingest import ingest_filing
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.llms.anthropic import Anthropic

load_dotenv()

st.set_page_config(page_title="Financial Report Analyst", page_icon="📈", layout="wide")

st.title("📈 Financial Report Analyst")
st.caption("Upload 10-K or 10-Q filings and ask questions across one or multiple companies.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("📁 Upload Filing")
    uploaded = st.file_uploader("10-K / 10-Q PDF", type=["pdf"])
    ticker = st.text_input("Company ticker", placeholder="AAPL, MSFT, GOOGL")

    if uploaded and ticker and st.button("Ingest Filing"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            tmp_path = Path(tmp.name)
        with st.spinner(f"Parsing {ticker} filing with LlamaParse..."):
            ingest_filing(tmp_path, ticker.upper())
            tmp_path.unlink(missing_ok=True)
        st.success(f"{ticker.upper()} filing indexed!")

storage = Path("./storage")
companies = [d.name for d in storage.iterdir() if d.is_dir()] if storage.exists() else []

if not companies:
    st.info("👈 Upload a filing in the sidebar to get started.")
    st.stop()

st.subheader("Indexed Companies")
selected = st.multiselect("Select companies to query", companies, default=companies[:2] if len(companies) >= 2 else companies)

if not selected:
    st.stop()

st.divider()
st.subheader("💬 Ask the Analyst")

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("e.g. What was the gross margin? How did revenue change YoY?")
if question and selected:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    llm = Anthropic(model="claude-sonnet-4-6", api_key=os.environ["ANTHROPIC_API_KEY"])
    all_nodes = []
    for company in selected:
        ctx = StorageContext.from_defaults(persist_dir=f"./storage/{company}")
        idx = load_index_from_storage(ctx)
        retriever = idx.as_retriever(similarity_top_k=4)
        all_nodes.extend(retriever.retrieve(question))

    context = "\n\n".join([f"[{n.metadata.get('company', '?')}]\n{n.text}" for n in all_nodes])
    with st.spinner("Analyzing filings..."):
        response = llm.complete(
            f"You are a financial analyst. Answer precisely using only the data below. "
            f"Always cite the company name next to each figure.\n\n{context}\n\nQuestion: {question}"
        )
    answer = str(response)
    st.session_state.history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)

if st.sidebar.button("Clear conversation"):
    st.session_state.history = []

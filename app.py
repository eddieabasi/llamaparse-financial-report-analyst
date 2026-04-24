import os
import streamlit as st
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.llms.anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Financial Report Analyst", layout="wide")
st.title("Financial Report Analyst")

companies = [d.name for d in Path("./storage").iterdir() if d.is_dir()] if Path("./storage").exists() else []

if not companies:
    st.warning("No filings indexed yet. Run `python ingest.py --file <pdf> --company <ticker>` first.")
    st.stop()

selected = st.multiselect("Select companies to query", companies, default=companies[:1])
question = st.text_input("Ask a question about the filings", placeholder="What was Apple's revenue growth YoY?")

if st.button("Ask") and question and selected:
    llm = Anthropic(model="claude-sonnet-4-6", api_key=os.environ["ANTHROPIC_API_KEY"])

    all_nodes = []
    for company in selected:
        ctx = StorageContext.from_defaults(persist_dir=f"./storage/{company}")
        idx = load_index_from_storage(ctx)
        retriever = idx.as_retriever(similarity_top_k=3)
        all_nodes.extend(retriever.retrieve(question))

    context = "\n\n".join([f"[{n.metadata.get('company')}]\n{n.text}" for n in all_nodes])

    with st.spinner("Analyzing..."):
        response = llm.complete(
            f"Answer using only the financial data below. Be precise with numbers.\n\n{context}\n\nQuestion: {question}"
        )
    st.markdown(str(response))

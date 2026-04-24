# LlamaParse — Financial Report Analyst (10-K / 10-Q)

An agent that parses SEC filings and earnings reports, extracts structured financial metrics, and enables natural-language Q&A and multi-company comparison.

## What it does
- Parses dense financial tables (income statement, balance sheet, cash flow) with high accuracy
- Extracts: revenue, gross margin, net income, EPS, guidance, risk factors
- Multi-company comparison: "Compare Apple vs Microsoft gross margin 2024 vs 2025"
- Trend detection across quarterly filings
- Export: structured JSON or Excel for financial models

## Stack
- **Parser:** LlamaParse (PDF → Markdown + JSON tables)
- **Extraction:** LlamaExtract + Pydantic schema
- **Vector store:** Weaviate (multi-tenancy per company)
- **LLM:** Claude Sonnet 4.6
- **UI:** Streamlit dashboard

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env   # add LLAMA_CLOUD_API_KEY, ANTHROPIC_API_KEY
python ingest.py --file ./filings/AAPL_10K_2025.pdf --company AAPL
streamlit run app.py
```

## Project structure
```
.
├── ingest.py            # Parse + extract + store filing
├── agent.py             # Multi-document ReAct agent
├── schema.py            # Pydantic financial metric schema
├── app.py               # Streamlit dashboard
├── requirements.txt
└── .env.example
```

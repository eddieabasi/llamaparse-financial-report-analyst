import os
import argparse
from pathlib import Path
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()


def ingest_filing(file_path: Path, company: str) -> None:
    parser = LlamaParse(
        api_key=os.environ["LLAMA_CLOUD_API_KEY"],
        result_type="markdown",
        parsing_instruction=(
            "Parse this SEC financial filing. Preserve all financial tables exactly, "
            "including income statement, balance sheet, and cash flow statement. "
            "Keep all numerical values and their units."
        ),
    )

    docs = parser.load_data(str(file_path))
    for doc in docs:
        doc.metadata["company"] = company
        doc.metadata["source"] = file_path.name

    splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=128)
    nodes = splitter.get_nodes_from_documents(docs)

    index = VectorStoreIndex(nodes)
    index.storage_context.persist(f"./storage/{company}")

    print(f"Indexed {len(nodes)} chunks for {company} from {file_path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--company", required=True)
    args = parser.parse_args()
    ingest_filing(Path(args.file), args.company)

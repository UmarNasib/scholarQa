import os
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from langchain_text_splitters import RecursiveCharacterTextSplitter

MODELS = create_model_dict()
CONVERTER = PdfConverter(artifact_dict=MODELS)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    add_start_index=True,
)

def ingest_and_chunk_pdf(filepath: str):
    try:
        rendered = CONVERTER(filepath)
        full_text, _, _ = text_from_rendered(rendered)
        return text_splitter.split_text(full_text)
    except Exception as e:
        print(f"Extraction Error: {e}")
        return None
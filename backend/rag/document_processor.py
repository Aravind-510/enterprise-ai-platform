import re
from pathlib import Path

import markdown
from bs4 import BeautifulSoup
from docx import Document
from pypdf import PdfReader


class DocumentProcessor:

    def __init__(self):
        pass

    # -----------------------------
    # Extract Text
    # -----------------------------
    def extract_text(self, file_path: str):

        file_path = Path(file_path)

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._read_pdf(file_path)

        elif suffix == ".docx":
            return self._read_docx(file_path)

        elif suffix == ".txt":
            return self._read_txt(file_path)

        elif suffix == ".md":
            return self._read_markdown(file_path)

        else:
            raise ValueError("Unsupported document type")

    # -----------------------------
    # PDF
    # -----------------------------
    def _read_pdf(self, path):

        reader = PdfReader(str(path))

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    # -----------------------------
    # DOCX
    # -----------------------------
    def _read_docx(self, path):

        doc = Document(path)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

        return text

    # -----------------------------
    # TXT
    # -----------------------------
    def _read_txt(self, path):

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # -----------------------------
    # Markdown
    # -----------------------------
    def _read_markdown(self, path):

        with open(path, "r", encoding="utf-8") as f:
            md = f.read()

        html = markdown.markdown(md)

        soup = BeautifulSoup(html, "html.parser")

        return soup.get_text()

    # -----------------------------
    # Clean Text
    # -----------------------------
    def clean_text(self, text):

        text = re.sub(r"\s+", " ", text)

        text = text.strip()

        return text

    # -----------------------------
    # Metadata
    # -----------------------------
    def extract_metadata(self, file_path):

        path = Path(file_path)

        return {

            "filename": path.name,

            "extension": path.suffix,

            "size": path.stat().st_size,

        }

    # -----------------------------
    # Chunking
    # -----------------------------
    def chunk_text(
        self,
        text,
        chunk_size=500,
        overlap=50
    ):

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk = words[start:end]

            chunks.append(" ".join(chunk))

            start += chunk_size - overlap

        return chunks

    # -----------------------------
    # Process Complete Document
    # -----------------------------
    def process_document(
        self,
        file_path,
        chunk_size=500,
        overlap=50
    ):

        raw_text = self.extract_text(file_path)

        cleaned_text = self.clean_text(raw_text)

        metadata = self.extract_metadata(file_path)

        chunks = self.chunk_text(
            cleaned_text,
            chunk_size,
            overlap
        )

        return {

            "metadata": metadata,

            "total_chunks": len(chunks),

            "chunks": chunks

        }


processor = DocumentProcessor()
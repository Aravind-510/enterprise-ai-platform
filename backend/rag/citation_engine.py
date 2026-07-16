"""
backend/rag/citation_engine.py

Enterprise Citation Engine
"""

from typing import List, Dict


class CitationEngine:

    def __init__(self):
        pass

    def generate_citations(self, retrieved_chunks: List[Dict]):

        citations = []

        for chunk in retrieved_chunks:

            metadata = chunk.get("metadata", {})

            citation = {
                "file_name": metadata.get("file", "Unknown"),
                "page_number": metadata.get("page", "N/A"),
                "section": metadata.get("section", "N/A"),
                "chunk_id": chunk.get("id", "N/A"),
                "similarity_score": round(
                    chunk.get("final_score", 0.0), 4
                ),
                "text": chunk.get("text", "")
            }

            citations.append(citation)

        return citations

    def format_citations(self, citations):

        output = []

        for citation in citations:

            formatted = f"""
According to:

File: {citation['file_name']}
Section: {citation['section']}
Page: {citation['page_number']}
Chunk ID: {citation['chunk_id']}
Similarity Score: {citation['similarity_score']}

{citation['text']}
"""

            output.append(formatted.strip())

        return "\n\n".join(output)


if __name__ == "__main__":

    retrieved_chunks = [

        {
            "id": "1",
            "text": "Employees are entitled to 20 days of annual leave every year.",
            "final_score": 0.9634,
            "metadata": {
                "file": "HR Policy.pdf",
                "page": 18,
                "section": "4.2"
            }
        },

        {
            "id": "2",
            "text": "Medical insurance covers employees and their dependents.",
            "final_score": 0.8745,
            "metadata": {
                "file": "Benefits.pdf",
                "page": 7,
                "section": "2.1"
            }
        }

    ]

    engine = CitationEngine()

    citations = engine.generate_citations(retrieved_chunks)

    print("\nGenerated Citations\n")

    print(engine.format_citations(citations))
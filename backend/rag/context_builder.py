"""
backend/rag/context_builder.py
Enterprise Context Builder
"""

from typing import List, Dict


class ContextBuilder:

    def __init__(self, max_tokens=1800):
        self.max_tokens = max_tokens

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))

    def remove_duplicates(self, chunks: List[Dict]) -> List[Dict]:
        unique = []
        seen = set()

        for chunk in chunks:
            text = chunk["text"].strip()

            if text not in seen:
                seen.add(text)
                unique.append(chunk)

        return unique

    def build_context(self, chunks: List[Dict]):

        chunks = self.remove_duplicates(chunks)

        context = []
        sources = []
        token_count = 0

        for chunk in chunks:

            tokens = self.estimate_tokens(chunk["text"])

            if token_count + tokens > self.max_tokens:
                break

            context.append(chunk["text"])

            sources.append(
                {
                    "file": chunk["metadata"]["file"],
                    "page": chunk["metadata"]["page"],
                    "section": chunk["metadata"]["section"],
                    "department": chunk["metadata"]["department"],
                }
            )

            token_count += tokens

        return {
            "context": context,
            "sources": sources,
            "token_count": token_count,
        }


if __name__ == "__main__":

    retrieved_chunks = [
        {
            "text": "Employees are entitled to 20 days of annual leave every year.",
            "metadata": {
                "file": "HR Policy.pdf",
                "page": 18,
                "section": "4.2",
                "department": "HR",
            },
        },
        {
            "text": "Medical insurance covers employees and their dependents.",
            "metadata": {
                "file": "Benefits.pdf",
                "page": 7,
                "section": "2.1",
                "department": "HR",
            },
        },
        {
            "text": "Employees are entitled to 20 days of annual leave every year.",
            "metadata": {
                "file": "HR Policy.pdf",
                "page": 18,
                "section": "4.2",
                "department": "HR",
            },
        },
    ]

    builder = ContextBuilder()

    result = builder.build_context(retrieved_chunks)

    print(result)
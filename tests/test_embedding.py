import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.rag.embedding_service import embedding_service

text = "Enterprise AI Platform"

result = embedding_service.generate_embedding(text)

print(result["model"])
print(result["dimension"])
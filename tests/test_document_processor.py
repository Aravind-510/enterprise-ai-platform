import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.document_processor import processor

result = processor.process_document("storage/documents/sample.txt")

print(result["metadata"])
print(result["total_chunks"])
print(result["chunks"][0])
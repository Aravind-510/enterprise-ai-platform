import time
import uuid

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):

        self.models = {
            "MiniLM": SentenceTransformer("all-MiniLM-L6-v2"),
            "BGE": SentenceTransformer("BAAI/bge-base-en-v1.5")
        }

    def generate_embedding(
        self,
        text,
        model_name="MiniLM"
    ):

        if model_name not in self.models:
            raise ValueError("Invalid embedding model")

        model = self.models[model_name]

        start_time = time.time()

        embedding = model.encode(text)

        end_time = time.time()

        processing_time = end_time - start_time

        return {

            "embedding_id": str(uuid.uuid4()),

            "model": model_name,

            "dimension": len(embedding),

            "processing_time": round(processing_time, 4),

            "embedding": embedding.tolist()

        }

    def batch_generate(
        self,
        chunks,
        model_name="MiniLM"
    ):

        results = []

        for chunk in chunks:

            result = self.generate_embedding(
                chunk,
                model_name
            )

            results.append(result)

        return results


embedding_service = EmbeddingService()
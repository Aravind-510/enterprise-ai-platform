import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(path="vector_db")

        departments = {
            "HR": "department_hr",
            "Payroll": "department_payroll",
            "Projects": "department_projects",
            "Engineering": "department_engineering",
            "Support": "department_support"
        }

        self.collections = {}

        for dept, collection_name in departments.items():
            self.collections[dept] = self.client.get_or_create_collection(
                name=collection_name
            )

    def insert_document(self, department, embedding_id, embedding, document, metadata):
        self.collections[department].add(
            ids=[embedding_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )

    def update_document(self, department, embedding_id, embedding, document, metadata):
        self.collections[department].update(
            ids=[embedding_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )

    def delete_document(self, department, embedding_id):
        self.collections[department].delete(ids=[embedding_id])

    def search(self, department, embedding, top_k=5):
        return self.collections[department].query(
            query_embeddings=[embedding],
            n_results=top_k
        )

    def search_with_filter(self, department, embedding, metadata_filter, top_k=5):
        return self.collections[department].query(
            query_embeddings=[embedding],
            where=metadata_filter,
            n_results=top_k
        )


vector_store = VectorStore()
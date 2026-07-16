import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.vector_store import vector_store


def test_insert():

    embedding = [0.1] * 384

    metadata = {
        "department": "HR",
        "owner": "Admin",
        "document": "Employee Handbook"
    }

    vector_store.insert_document(
        department="HR",
        embedding_id="emp001",
        embedding=embedding,
        document="Employee Handbook Version 1",
        metadata=metadata
    )

    print("Insert Test Passed")


def test_search():

    embedding = [0.1] * 384

    results = vector_store.search(
        department="HR",
        embedding=embedding,
        top_k=5
    )

    print("\nSearch Results")
    print(results)


def test_update():

    embedding = [0.2] * 384

    metadata = {
        "department": "HR",
        "owner": "Manager",
        "document": "Employee Handbook Updated"
    }

    vector_store.update_document(
        department="HR",
        embedding_id="emp001",
        embedding=embedding,
        document="Employee Handbook Version 2",
        metadata=metadata
    )

    print("\nUpdate Test Passed")


def test_delete():

    vector_store.delete_document(
        department="HR",
        embedding_id="emp001"
    )

    print("\nDelete Test Passed")


if __name__ == "__main__":

    print("=" * 50)
    print("Testing ChromaDB Vector Store")
    print("=" * 50)

    test_insert()

    test_search()

    test_update()

    test_search()

    test_delete()

    print("\nAll Tests Completed Successfully")
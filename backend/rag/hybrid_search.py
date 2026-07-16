"""
backend/rag/hybrid_search.py
Simplified Enterprise Hybrid Search
"""

import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

SEARCH_CONFIG = {
    "semantic_weight": 0.65,
    "keyword_weight": 0.35,
    "top_k": 5,
}

documents = [
    {"id":"1","text":"Employees are entitled to 20 days of annual leave every year.","department":"HR","file":"HR Policy.pdf","page":18,"section":"4.2"},
    {"id":"2","text":"Medical insurance covers employees and their dependents.","department":"HR","file":"Benefits.pdf","page":7,"section":"2.1"},
    {"id":"3","text":"Developers must follow secure coding standards.","department":"Engineering","file":"Engineering Handbook.pdf","page":35,"section":"8.3"},
    {"id":"4","text":"VPN access is mandatory for remote employees.","department":"IT","file":"Security Policy.pdf","page":12,"section":"3.4"},
    {"id":"5","text":"Expense reimbursement should be submitted within 30 days.","department":"Finance","file":"Finance Policy.pdf","page":10,"section":"5.1"},
]

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection("enterprise_documents")

try:
    if collection.count() == 0:
        collection.add(
            ids=[d["id"] for d in documents],
            documents=[d["text"] for d in documents],
            embeddings=model.encode([d["text"] for d in documents]).tolist(),
            metadatas=[{
                "department":d["department"],
                "file":d["file"],
                "page":d["page"],
                "section":d["section"]
            } for d in documents]
        )
except Exception:
    pass

bm25 = BM25Okapi([d["text"].lower().split() for d in documents])

def semantic_search(query, top_k=10):
    emb=model.encode(query).tolist()
    r=collection.query(query_embeddings=[emb],n_results=top_k)
    out=[]
    for i in range(len(r["ids"][0])):
        out.append({
            "id":r["ids"][0][i],
            "text":r["documents"][0][i],
            "metadata":r["metadatas"][0][i],
            "semantic_score":1/(1+r["distances"][0][i])
        })
    return out

def keyword_search(query, top_k=10):
    scores=bm25.get_scores(query.lower().split())
    res=[]
    for i,s in enumerate(scores):
        res.append({
            "id":documents[i]["id"],
            "text":documents[i]["text"],
            "metadata":{
                "department":documents[i]["department"],
                "file":documents[i]["file"],
                "page":documents[i]["page"],
                "section":documents[i]["section"],
            },
            "keyword_score":float(s)
        })
    m=max([x["keyword_score"] for x in res]) or 1
    for x in res:
        x["keyword_score"]/=m
    return sorted(res,key=lambda x:x["keyword_score"],reverse=True)[:top_k]

def filter_department(results, department=None):
    return results if not department else [r for r in results if r["metadata"]["department"].lower()==department.lower()]

def filter_metadata(results, filters=None):
    if not filters:
        return results
    out=[]
    for r in results:
        if all(str(r["metadata"].get(k,"")).lower()==str(v).lower() for k,v in filters.items()):
            out.append(r)
    return out

def hybrid_search(query, department=None, metadata_filters=None,
                  semantic_weight=0.65, keyword_weight=0.35, top_k=5):
    sem=semantic_search(query,30)
    key=keyword_search(query,30)
    merged={}
    for x in sem:
        merged[x["id"]]={"id":x["id"],"text":x["text"],"metadata":x["metadata"],
                         "semantic_score":x["semantic_score"],"keyword_score":0}
    for x in key:
        merged.setdefault(x["id"],{"id":x["id"],"text":x["text"],"metadata":x["metadata"],
                                   "semantic_score":0,"keyword_score":0})
        merged[x["id"]]["keyword_score"]=x["keyword_score"]
    res=[]
    for v in merged.values():
        v["final_score"]=semantic_weight*v["semantic_score"]+keyword_weight*v["keyword_score"]
        res.append(v)
    res=sorted(res,key=lambda x:x["final_score"],reverse=True)
    res=filter_department(res,department)
    res=filter_metadata(res,metadata_filters)
    return res[:top_k]

def search(query, department=None, metadata_filters=None):
    return {
        "query":query,
        "results":hybrid_search(query,department,metadata_filters,
                                SEARCH_CONFIG["semantic_weight"],
                                SEARCH_CONFIG["keyword_weight"],
                                SEARCH_CONFIG["top_k"])
    }

if __name__=="__main__":
    r=search("leave policy",department="HR")
    for x in r["results"]:
        print(x)

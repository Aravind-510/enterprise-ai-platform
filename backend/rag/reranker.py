"""backend/rag/reranker.py"""
import time
from sentence_transformers import CrossEncoder
from backend.rag.hybrid_search import hybrid_search
MODEL_NAME="cross-encoder/ms-marco-MiniLM-L-6-v2"
class EnterpriseReranker:
    def __init__(self):
        self.model=CrossEncoder(MODEL_NAME)
    def rerank(self,query,candidates,top_k=5):
        pairs=[(query,c["text"]) for c in candidates]
        scores=self.model.predict(pairs)
        out=[]
        for c,s in zip(candidates,scores):
            d=c.copy(); d["reranker_score"]=float(s); out.append(d)
        return sorted(out,key=lambda x:x["reranker_score"],reverse=True)[:top_k]
def generate_report(query,retrieval_ms,rerank_ms,results):
    md=f"# Reranker Evaluation Report\n\nQuery: {query}\n\nRetrieval: {retrieval_ms:.2f} ms\nRe-ranking: {rerank_ms:.2f} ms\n\n"
    for i,r in enumerate(results,1):
        md+=f"{i}. {r['metadata']['file']} - {r['reranker_score']:.4f}\n"
    return md
if __name__=="__main__":
    q="leave policy"
    t=time.perf_counter(); c=hybrid_search(q,top_k=30); rt=(time.perf_counter()-t)*1000
    rr=EnterpriseReranker()
    t=time.perf_counter(); top=rr.rerank(q,c,5); rrt=(time.perf_counter()-t)*1000
    for r in top: print(r)
    import os; os.makedirs("evaluation",exist_ok=True)
    open("evaluation/reranker_report.md","w",encoding="utf-8").write(generate_report(q,rt,rrt,top))

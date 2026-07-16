"""
backend/rag/query_rewriter.py
Enterprise Query Rewriter
"""

from nltk.corpus import wordnet as wn
import nltk

try:
    wn.synsets("test")
except LookupError:
    nltk.download("wordnet")
    nltk.download("omw-1.4")

ACRONYMS = {
    "hr": "Human Resources",
    "vpn": "Virtual Private Network",
    "it": "Information Technology",
    "ai": "Artificial Intelligence",
    "ml": "Machine Learning",
}

DOMAIN_REWRITES = {
    "leave policy": [
        "employee annual leave policy",
        "vacation policy",
        "leave entitlement",
        "leave guidelines",
    ],
    "security": [
        "information security policy",
        "cyber security guidelines",
    ],
}

def synonyms(term):
    words=set()
    for syn in wn.synsets(term):
        for l in syn.lemmas():
            w=l.name().replace("_"," ")
            if w.lower()!=term.lower():
                words.add(w)
    return sorted(words)[:10]

def expand_acronyms(query):
    parts=[]
    for w in query.split():
        parts.append(ACRONYMS.get(w.lower(), w))
    return " ".join(parts)

def rewrite_query(query):
    rewrites=[]
    expanded=expand_acronyms(query)
    if expanded!=query:
        rewrites.append(expanded)
    if query.lower() in DOMAIN_REWRITES:
        rewrites.extend(DOMAIN_REWRITES[query.lower()])
    for word in query.split():
        for s in synonyms(word):
            rewrites.append(query.replace(word,s))
    seen=[]
    for r in [query]+rewrites:
        if r not in seen:
            seen.append(r)
    return seen

if __name__=="__main__":
    q=input("Enter query: ")
    print("\nRewritten Queries:")
    for i,r in enumerate(rewrite_query(q),1):
        print(f"{i}. {r}")

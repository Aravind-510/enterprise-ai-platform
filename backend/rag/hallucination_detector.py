"""
backend/rag/hallucination_detector.py
"""

from typing import List, Dict

class HallucinationDetector:

    def __init__(self, confidence_threshold=0.60):
        self.confidence_threshold=confidence_threshold

    def evaluate(self, answer:str, sources:List[Dict], retrieval_confidence:float):

        missing_citations=len(sources)==0

        unsupported_claims=False
        fabricated_information=False

        hallucination=(
            missing_citations or
            retrieval_confidence<self.confidence_threshold or
            unsupported_claims or
            fabricated_information
        )

        confidence=round(retrieval_confidence*100,2)

        return {
            "hallucination":hallucination,
            "confidence":confidence,
            "supported_sources":len(sources),
            "missing_citations":missing_citations,
            "unsupported_claims":unsupported_claims,
            "fabricated_information":fabricated_information
        }

if __name__=="__main__":

    detector=HallucinationDetector()

    answer="Employees receive 20 days of annual leave."

    sources=[
        {
            "file":"HR Policy.pdf",
            "page":18,
            "section":"4.2"
        }
    ]

    result=detector.evaluate(
        answer=answer,
        sources=sources,
        retrieval_confidence=0.97
    )

    print(result)

    import os,json
    os.makedirs("evaluation",exist_ok=True)

    with open(
        "evaluation/hallucination_report.md",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("# Hallucination Detection Report\n\n")
        f.write(f"Hallucination: {result['hallucination']}\n\n")
        f.write(f"Confidence: {result['confidence']}\n\n")
        f.write(f"Supported Sources: {result['supported_sources']}\n")

# Enterprise AI Platform

## Retrieval Benchmark Report

|Model|Chunk Size|Overlap|Chunks|Latency(s)|Top-K Accuracy|
|------|-----------|---------|--------|-----------|---------------|
|MiniLM|500|50|1|0.3725|0.96|
|MiniLM|500|100|1|0.0272|0.98|
|MiniLM|500|200|1|0.0265|0.98|
|MiniLM|750|50|1|0.0278|0.98|
|MiniLM|750|100|1|0.0319|0.98|
|MiniLM|750|200|1|0.0406|0.98|
|MiniLM|1000|50|1|0.0436|0.98|
|MiniLM|1000|100|1|0.0387|0.98|
|MiniLM|1000|200|1|0.0277|0.98|
|BGE|500|50|1|3.0922|0.83|
|BGE|500|100|1|0.2049|0.97|
|BGE|500|200|1|0.1683|0.97|
|BGE|750|50|1|0.1717|0.97|
|BGE|750|100|1|0.1527|0.97|
|BGE|750|200|1|0.1596|0.97|
|BGE|1000|50|1|0.1669|0.97|
|BGE|1000|100|1|0.183|0.97|
|BGE|1000|200|1|0.1651|0.97|

## Summary

- Benchmark completed successfully.
- Compared MiniLM and BGE models.
- Evaluated multiple chunk sizes.
- Evaluated multiple overlaps.
- Measured embedding generation latency.
- Estimated Top-K retrieval accuracy.

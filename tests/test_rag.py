from oracle.rag.chunking import chunk_text
from oracle.rag.store import build_index, search


def test_chunking_splits_and_labels_sources():
    text = "Para one.\n\n" + ("Long sentence. " * 100)
    chunks = chunk_text(text, source="doc.md", max_chars=200, overlap=20)
    assert len(chunks) > 2
    assert chunks[0].id == "doc.md#0"
    assert all(len(c.text) <= 200 for c in chunks)


def test_tfidf_search_finds_relevant_chunk(tmp_path):
    chunks = chunk_text("Refunds are issued within 7 days.\n\nShipping takes 5 days by road.", "a.md",
                        max_chars=40, overlap=5)
    path = build_index(chunks, index_path=tmp_path / "idx.json", backend="tfidf")
    results = search("when do refunds happen", k=1, index_path=path)
    assert results and "Refunds" in results[0]["text"]

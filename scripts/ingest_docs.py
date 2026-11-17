"""Chunk everything in DOCS_DIR and build the retrieval index."""
from oracle.config import get_settings
from oracle.rag.chunking import chunk_text
from oracle.rag.store import build_index


def main() -> None:
    cfg = get_settings()
    chunks = []
    for path in sorted(cfg.docs_dir.glob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            chunks.extend(chunk_text(path.read_text(encoding="utf-8"), source=path.name))
    if not chunks:
        raise SystemExit(f"No .md/.txt documents found in {cfg.docs_dir}")
    out = build_index(chunks)
    print(f"Indexed {len(chunks)} chunks ({cfg.retriever_backend}) -> {out}")


if __name__ == "__main__":
    main()

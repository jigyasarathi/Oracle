from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    text: str


def chunk_text(text: str, source: str, max_chars: int = 800, overlap: int = 100) -> list[Chunk]:
    """Paragraph-aware chunking. Long paragraphs are split with a small overlap."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    pieces: list[str] = []
    buffer = ""
    for para in paragraphs:
        if len(para) > max_chars:
            if buffer:
                pieces.append(buffer)
                buffer = ""
            start = 0
            while start < len(para):
                pieces.append(para[start : start + max_chars])
                start += max_chars - overlap
        elif len(buffer) + len(para) + 2 <= max_chars:
            buffer = f"{buffer}\n\n{para}".strip()
        else:
            pieces.append(buffer)
            buffer = para
    if buffer:
        pieces.append(buffer)
    return [Chunk(id=f"{source}#{i}", source=source, text=p) for i, p in enumerate(pieces)]

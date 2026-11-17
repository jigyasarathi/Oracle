"""Ask ORACLE a question from the command line: python scripts/ask.py "your question" """
import asyncio
import json
import sys

from oracle.service import ask


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scripts/ask.py "your question"')
    result = asyncio.run(ask(" ".join(sys.argv[1:])))
    print(result["answer"])
    print("\n--- metrics ---")
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()

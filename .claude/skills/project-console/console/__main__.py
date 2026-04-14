import sys

import uvicorn


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] != "serve":
        print("Usage: python -m console serve", file=sys.stderr)
        sys.exit(1)
    uvicorn.run("console.app:app", host="127.0.0.1", port=8765, reload=True)


if __name__ == "__main__":
    main()

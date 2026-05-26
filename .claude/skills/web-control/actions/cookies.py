"""`/web-control cookies <url-or-domain> [--format=header|json] [--show-values]`

Extract cookies from the debug Chrome's cookie jar for a given URL or domain.
The output is suitable for use as a `Cookie:` request header (default) or as
JSON for downstream tooling.

Use cases:
    - A consumer skill needs to make authenticated REST calls to a service
      whose API the user has signed into via the debug Chrome (e.g.,
      Atlassian Confluence attachment endpoints, which the official
      Atlassian MCP does not expose).
    - The debug Chrome's cookie jar is the auth surface; this action is
      the bridge from interactive sign-in to programmatic HTTP.

Examples:
    /web-control cookies example.atlassian.net
    /web-control cookies https://example.com/path --format=json
    /web-control cookies example.atlassian.net --show-values   # full values

Security note:
    Cookie values are sensitive (session tokens). By default this command
    redacts values to length-only summaries. Pass `--show-values` to print
    the raw `Cookie:` header — only do so when piping into a controlled
    consumer (e.g., a sibling Python lib reading stdout). Never paste the
    output into chat or logs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.cookies import cookies_to_header, extract_cookies  # noqa: E402
from lib.errors import ChromeNotRunning, WebControlError  # noqa: E402
from lib.platform import DEFAULT_DEBUG_PORT  # noqa: E402


def _redact(value: str) -> str:
    n = len(value)
    if n <= 8:
        return f"<{n} chars>"
    return f"{value[:4]}…<{n} chars>"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="web-control cookies",
        description="Extract cookies from the debug Chrome jar for a URL/domain.",
    )
    parser.add_argument(
        "url_or_domain",
        help="Target URL or bare domain (e.g. example.atlassian.net).",
    )
    parser.add_argument(
        "--format",
        choices=("header", "json", "summary"),
        default="summary",
        help="Output format. summary (default): redacted human-readable list. "
             "header: 'name=val; name=val' Cookie header. json: raw CDP cookie array.",
    )
    parser.add_argument(
        "--show-values",
        action="store_true",
        help="Print raw cookie values. By default values are redacted.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_DEBUG_PORT,
        help=f"Debug Chrome port (default: {DEFAULT_DEBUG_PORT}).",
    )
    args = parser.parse_args(argv)

    try:
        cookies = extract_cookies(args.url_or_domain, port=args.port)
    except ChromeNotRunning as exc:
        print(f"web-control cookies: {exc}", file=sys.stderr)
        print(
            "  -> Run: /web-control launch  (then sign in to the target site, "
            "checking 'Remember me' / 'Stay signed in' so the session persists).",
            file=sys.stderr,
        )
        return 1
    except WebControlError as exc:
        print(exc.render(), file=sys.stderr)
        return 1

    if not cookies:
        print(
            f"web-control cookies: no cookies found for {args.url_or_domain}.",
            file=sys.stderr,
        )
        print(
            "  -> Open the site in the debug Chrome (/web-control launch), "
            "sign in (check 'Remember me'), then re-run this command.",
            file=sys.stderr,
        )
        return 2

    if args.format == "json":
        print(json.dumps(cookies, indent=2, sort_keys=True))
        return 0

    if args.format == "header":
        if not args.show_values:
            print(
                "web-control cookies: refusing to print 'header' format with "
                "redacted values (would be unusable). Pass --show-values to "
                "emit the raw Cookie header (sensitive — pipe directly into "
                "your consumer, do not paste into chat/logs).",
                file=sys.stderr,
            )
            return 64
        print(cookies_to_header(cookies))
        return 0

    # summary (default) — redacted, human-readable
    print(f"# {len(cookies)} cookies for {args.url_or_domain}")
    for c in cookies:
        name = c.get("name", "")
        value = c.get("value", "")
        domain = c.get("domain", "")
        path = c.get("path", "/")
        secure = "S" if c.get("secure") else "-"
        http_only = "H" if c.get("httpOnly") else "-"
        same_site = c.get("sameSite", "")[:1] or "-"
        flags = f"[{secure}{http_only}{same_site}]"
        rendered = value if args.show_values else _redact(value)
        print(f"  {flags} {domain}{path}  {name} = {rendered}")
    if not args.show_values:
        print(
            "\n# Values redacted. Pass --show-values to print raw values, "
            "or --format=header --show-values to emit a Cookie request header.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except WebControlError as exc:
        print(exc.render(), file=sys.stderr)
        sys.exit(1)

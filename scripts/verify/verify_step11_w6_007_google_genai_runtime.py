from __future__ import annotations

from importlib.metadata import version

from google import genai
from google.genai import errors, types


def main() -> int:
    installed = version("google-genai")
    if installed != "2.28.0":
        raise SystemExit(f"unexpected google-genai version: {installed}")
    if not callable(genai.Client):
        raise SystemExit("google.genai.Client is unavailable")
    if not issubclass(errors.APIError, Exception):
        raise SystemExit("google.genai.errors.APIError is unavailable")
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema={"type": "object"},
    )
    if config.response_mime_type != "application/json":
        raise SystemExit("google-genai structured output config unavailable")
    print("google-genai runtime PASS: 2.28.0 / async client + structured output API importable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

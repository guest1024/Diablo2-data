from __future__ import annotations

import re
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from crawler.models import FetchResponse


DEFAULT_CHARSETS = ("utf-8", "gb18030", "gbk", "gb2312", "latin1")


def decode_bytes(body: bytes, content_type: str | None, hints: Iterable[str]) -> str:
    charsets: list[str] = []
    if content_type:
        match = re.search(r"charset=([^;]+)", content_type, re.I)
        if match:
            charsets.append(match.group(1).strip())
    charsets.extend(hints)
    charsets.extend(DEFAULT_CHARSETS)

    seen: set[str] = set()
    for charset in charsets:
        normalized = charset.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        try:
            return body.decode(charset)
        except Exception:
            continue
    return body.decode("utf-8", "ignore")


class HttpFetcher:
    def __init__(self, user_agent: str, timeout: int) -> None:
        self.user_agent = user_agent
        self.timeout = timeout

    def fetch(self, url: str) -> FetchResponse:
        request = Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return FetchResponse(
                    url=response.geturl(),
                    status=response.status,
                    content_type=response.headers.get("Content-Type"),
                    body=response.read(),
                )
        except HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            return FetchResponse(
                url=url,
                status=exc.code,
                content_type=exc.headers.get("Content-Type"),
                body=body,
                note=str(exc),
            )
        except URLError as exc:
            return FetchResponse(url=url, status=None, content_type=None, body=b"", note=str(exc.reason))
        except Exception as exc:  # pragma: no cover
            return FetchResponse(url=url, status=None, content_type=None, body=b"", note=str(exc))


class RobotsManager:
    def __init__(self, fetcher: HttpFetcher) -> None:
        self.fetcher = fetcher
        self._cache: dict[str, tuple[RobotFileParser | None, str]] = {}

    def _load(self, robots_url: str) -> tuple[RobotFileParser | None, str]:
        if robots_url in self._cache:
            return self._cache[robots_url]

        response = self.fetcher.fetch(robots_url)
        if response.status != 200:
            result = (None, response.note or f"robots-unavailable:{response.status}")
            self._cache[robots_url] = result
            return result

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(decode_bytes(response.body, response.content_type, ("utf-8", "gb18030", "gbk", "gb2312")).splitlines())
        result = (parser, "ok")
        self._cache[robots_url] = result
        return result

    def can_fetch(self, robots_url: str | None, url: str) -> tuple[bool, str]:
        if not robots_url:
            return True, "no-robots-configured"

        parser, note = self._load(robots_url)
        if parser is None:
            return True, f"robots-best-effort:{note}"
        return parser.can_fetch(self.fetcher.user_agent, url), note

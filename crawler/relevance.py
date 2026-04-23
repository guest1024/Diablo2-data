from __future__ import annotations

from crawler.models import SourceConfig

GLOBAL_EXCLUDE_KEYWORDS = (
    "交易",
    "卖号",
    "賣號",
    "交友",
    "征婚",
    "陪玩",
    "代练",
    "估价",
    "拍卖",
    "收号",
    "出售账号",
    "出售帳號",
    "rmt",
    "bot交易",
)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords if keyword)


def is_relevant_page(source: SourceConfig, url: str, title: str, text: str) -> tuple[bool, str | None]:
    if _contains_any(url, source.relevance.exclude_url_keywords):
        return False, "excluded-by-url-keyword"
    if _contains_any(title, (*GLOBAL_EXCLUDE_KEYWORDS, *source.relevance.exclude_title_keywords)):
        return False, "excluded-by-title-keyword"
    if _contains_any(text, source.relevance.exclude_text_keywords):
        return False, "excluded-by-text-keyword"
    return True, None

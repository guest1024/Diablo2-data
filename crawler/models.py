from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DiscoveryRules:
    same_host: bool = True
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class SelectionRules:
    prefer_curated: bool = True
    preferred_keywords: tuple[str, ...] = ()
    denied_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class SnapshotRules:
    immutable_after_capture: bool = True
    store_raw_content: bool = True


@dataclass(frozen=True)
class RelevanceRules:
    exclude_url_keywords: tuple[str, ...] = ()
    exclude_title_keywords: tuple[str, ...] = ()
    exclude_text_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceConfig:
    id: str
    label: str
    enabled: bool
    weight: float
    region: str
    transport: str
    observed_on: str
    observed_status: str
    home_url: str
    robots_url: str | None
    authority_tier: str = "guide"
    lane: str = "guide"
    language: str = "zh"
    encoding_hints: tuple[str, ...] = ()
    seed_urls: tuple[str, ...] = ()
    curated_urls: tuple[str, ...] = ()
    discovery: DiscoveryRules = field(default_factory=DiscoveryRules)
    selection: SelectionRules = field(default_factory=SelectionRules)
    snapshot: SnapshotRules = field(default_factory=SnapshotRules)
    relevance: RelevanceRules = field(default_factory=RelevanceRules)
    notes: str | None = None

    @classmethod
    def from_dict(cls, payload: dict) -> "SourceConfig":
        discovery = payload.get("discovery", {})
        selection = payload.get("selection", {})
        snapshot = payload.get("snapshot", {})
        relevance = payload.get("relevance", {})
        return cls(
            id=payload["id"],
            label=payload["label"],
            enabled=payload.get("enabled", True),
            weight=float(payload["weight"]),
            region=payload["region"],
            transport=payload["transport"],
            observed_on=payload["observed_on"],
            observed_status=payload["observed_status"],
            home_url=payload["home_url"],
            robots_url=payload.get("robots_url"),
            authority_tier=payload.get("authority_tier", "guide"),
            lane=payload.get("lane", payload.get("authority_tier", "guide")),
            language=payload.get("language", "zh"),
            encoding_hints=tuple(payload.get("encoding_hints", [])),
            seed_urls=tuple(payload.get("seed_urls", [])),
            curated_urls=tuple(payload.get("curated_urls", [])),
            discovery=DiscoveryRules(
                same_host=discovery.get("same_host", True),
                include=tuple(discovery.get("include", [])),
                exclude=tuple(discovery.get("exclude", [])),
            ),
            selection=SelectionRules(
                prefer_curated=selection.get("prefer_curated", True),
                preferred_keywords=tuple(selection.get("preferred_keywords", [])),
                denied_keywords=tuple(selection.get("denied_keywords", [])),
            ),
            snapshot=SnapshotRules(
                immutable_after_capture=snapshot.get("immutable_after_capture", True),
                store_raw_content=snapshot.get("store_raw_content", True),
            ),
            relevance=RelevanceRules(
                exclude_url_keywords=tuple(relevance.get("exclude_url_keywords", [])),
                exclude_title_keywords=tuple(relevance.get("exclude_title_keywords", [])),
                exclude_text_keywords=tuple(relevance.get("exclude_text_keywords", [])),
            ),
            notes=payload.get("notes"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CrawlerConfig:
    version: str
    user_agent: str
    policy: dict
    sources: tuple[SourceConfig, ...]

    @classmethod
    def from_dict(cls, payload: dict) -> "CrawlerConfig":
        return cls(
            version=payload.get("version", "unknown"),
            user_agent=payload.get("user_agent", "Mozilla/5.0"),
            policy=payload.get("policy", {}),
            sources=tuple(SourceConfig.from_dict(source) for source in payload.get("sources", [])),
        )


@dataclass(frozen=True)
class CrawlOptions:
    config_path: Path
    timeout: int = 12
    limit_per_source: int = 2
    max_discover: int = 12
    probe_only: bool = False
    include_disabled: bool = False
    refresh_existing: bool = False
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class FetchResponse:
    url: str
    status: int | None
    content_type: str | None
    body: bytes
    note: str | None = None

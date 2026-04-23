from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crawler.catalog import classify_page, get_catalog_entry, load_page_catalog, update_page_catalog
from crawler.config import load_config
from crawler.extractors import extract_page_fields
from crawler.http_client import HttpFetcher, RobotsManager
from crawler.models import CrawlOptions, SourceConfig
from crawler.relevance import is_relevant_page
from crawler.selection import discover_urls, normalize_urls, select_candidates, sha256_bytes
from crawler.storage import save_snapshot, write_json, write_jsonl

CRAWLER_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = CRAWLER_ROOT / "sources.zh.json"
PAGE_CATALOG_PATH = CRAWLER_ROOT / "state/page_catalog.json"
SNAPSHOT_ROOT = CRAWLER_ROOT / "snapshots"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def timestamp_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def summarize_status(seed_records: list[dict[str, Any]], page_records: list[dict[str, Any]], probe_only: bool) -> str:
    if any(record.get("http_status") == 200 for record in page_records):
        return "probed" if probe_only else "captured"
    if any(record.get("capture_status") in {"frozen", "ignored"} for record in page_records):
        return "catalog-only"
    if any(record.get("status") == 200 for record in seed_records):
        return "seed-only"
    if any(record.get("status") == "robots-blocked" for record in [*seed_records, *page_records]):
        return "robots-limited"
    return "unreachable"


def render_summary(run_manifest: dict[str, Any]) -> str:
    lines = [
        "# 中文站点网页路径快照报告",
        "",
        f"- 生成时间: `{run_manifest['generated_at']}`",
        f"- 运行目录: `{run_manifest['run_dir']}`",
        f"- probe_only: `{run_manifest['probe_only']}`",
        f"- refresh_existing: `{run_manifest['refresh_existing']}`",
        "",
        "## 来源摘要",
        "",
        "| Source | Weight | Seeds | Candidates | New | Updated | Frozen | Ignored | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for source in run_manifest["sources"]:
        lines.append(
            f"| {source['label']} | {source['weight']:.2f} | {source['seed_count']} | {source['candidate_count']} | {source['new_count']} | {source['updated_count']} | {source['frozen_count']} | {source['ignored_count']} | {source['status']} |"
        )
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "1. 只保存网页路径快照、页面标题、HTTP 状态与快照文件映射。",
            "2. 默认对已抓取静态文章启用冻结机制：首次抓取后不再重复读取正文。",
            "3. 交友、卖号、交易、估价、拍卖等无关页面会过滤并进入 ignored 状态。",
            "4. `page_catalog.json` 维护 `url -> snapshot_path -> metadata` 的长期关系。",
            "",
        ]
    )
    return "\n".join(lines)


def resolve_sources(config_sources: tuple[SourceConfig, ...], options: CrawlOptions) -> list[SourceConfig]:
    sources = list(config_sources)
    if options.source_ids:
        wanted = set(options.source_ids)
        sources = [source for source in sources if source.id in wanted]
    if not options.include_disabled:
        sources = [source for source in sources if source.enabled]
    return sources


def should_skip_existing(existing: dict[str, Any] | None, source: SourceConfig, options: CrawlOptions) -> bool:
    if existing is None:
        return False
    if options.refresh_existing or not source.snapshot.immutable_after_capture:
        return False
    return existing.get("capture_status") in {"saved", "filtered"}


def build_page_record(
    source: SourceConfig,
    url: str,
    seen_at: str,
    run_id: str,
    *,
    title: str = "",
    http_status: int | None = None,
    content_type: str | None = None,
    sha256: str | None = None,
    robots_note: str = "",
    note: str | None = None,
    lifecycle_status: str | None = None,
    capture_status: str | None = None,
    snapshot_id: str | None = None,
    snapshot_path: str | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source.id,
        "source_label": source.label,
        "authority_tier": source.authority_tier,
        "lane": source.lane,
        "url": url,
        "title": title,
        "http_status": http_status,
        "content_type": content_type,
        "sha256": sha256,
        "robots_note": robots_note,
        "note": note,
        "lifecycle_status": lifecycle_status,
        "capture_status": capture_status,
        "snapshot_id": snapshot_id,
        "snapshot_path": snapshot_path,
        "seen_at": seen_at,
        "run_id": run_id,
    }


def build_frozen_record(source: SourceConfig, existing: dict[str, Any], seen_at: str, run_id: str) -> dict[str, Any]:
    capture_status = "ignored" if existing.get("capture_status") == "filtered" else "frozen"
    lifecycle_status = "ignored" if capture_status == "ignored" else "frozen"
    return build_page_record(
        source,
        existing["url"],
        seen_at,
        run_id,
        title=existing.get("title", ""),
        http_status=existing.get("http_status"),
        content_type=existing.get("content_type"),
        sha256=existing.get("sha256"),
        note="skipped-existing-catalog-entry",
        lifecycle_status=lifecycle_status,
        capture_status=capture_status,
        snapshot_id=existing.get("snapshot_id"),
        snapshot_path=existing.get("snapshot_path"),
    )


def process_source(
    source: SourceConfig,
    options: CrawlOptions,
    fetcher: HttpFetcher,
    robots: RobotsManager,
    page_catalog: dict[str, dict[str, Any]],
    run_id: str,
    seen_at: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    seed_urls = normalize_urls([*source.curated_urls, *source.seed_urls])
    seed_records: list[dict[str, Any]] = []
    discovered_urls: list[str] = []

    for seed_url in seed_urls:
        allowed, robots_note = robots.can_fetch(source.robots_url, seed_url)
        if not allowed:
            seed_records.append({"url": seed_url, "status": "robots-blocked", "robots_note": robots_note})
            continue

        response = fetcher.fetch(seed_url)
        record = {
            "url": seed_url,
            "status": response.status,
            "content_type": response.content_type,
            "note": response.note,
            "robots_note": robots_note,
            "bytes": len(response.body),
        }
        if response.status == 200:
            found = discover_urls(source, seed_url, response, options.max_discover)
            record["discovered_candidates"] = found[:10]
            discovered_urls.extend(found)
        seed_records.append(record)

    candidates = select_candidates(source, discovered_urls, options.limit_per_source)
    page_records: list[dict[str, Any]] = []
    catalog_updates: list[dict[str, Any]] = []
    retained_count = 0

    for url in candidates:
        if retained_count >= options.limit_per_source:
            break
        existing = get_catalog_entry(page_catalog, source.id, url)
        if should_skip_existing(existing, source, options):
            frozen_record = build_frozen_record(source, existing, seen_at, run_id)
            page_records.append(frozen_record)
            catalog_updates.append(frozen_record)
            retained_count += 1
            continue

        allowed, robots_note = robots.can_fetch(source.robots_url, url)
        if not allowed:
            page_records.append(
                build_page_record(
                    source,
                    url,
                    seen_at,
                    run_id,
                    robots_note=robots_note,
                    lifecycle_status="robots-blocked",
                    capture_status="robots-blocked",
                )
            )
            continue

        response = fetcher.fetch(url)
        title = ""
        text = ""
        sha_value = None
        lifecycle_status = None
        snapshot_key = None
        snapshot_path = None
        capture_status = None
        note = response.note

        if response.status == 200:
            title, text = extract_page_fields(response.body, response.content_type, source.encoding_hints)
            relevant, relevance_reason = is_relevant_page(source, url, title, text)
            if not relevant:
                capture_status = "filtered"
                lifecycle_status = "ignored"
                note = relevance_reason
            else:
                sha_value = sha256_bytes(response.body)
                lifecycle_status = classify_page(page_catalog, source.id, url, sha_value)
                if not options.probe_only and source.snapshot.store_raw_content:
                    snapshot_key, saved_path = save_snapshot(SNAPSHOT_ROOT, source.id, url, response.content_type, response.body)
                    snapshot_path = safe_relative(saved_path, CRAWLER_ROOT)
                    capture_status = "saved"
                else:
                    capture_status = "probed"

        record = build_page_record(
            source,
            url,
            seen_at,
            run_id,
            title=title,
            http_status=response.status,
            content_type=response.content_type,
            sha256=sha_value,
            robots_note=robots_note,
            note=note,
            lifecycle_status=lifecycle_status,
            capture_status=capture_status,
            snapshot_id=snapshot_key,
            snapshot_path=snapshot_path,
        )
        page_records.append(record)
        if response.status == 200:
            catalog_updates.append(record)
            if record.get('capture_status') in {'saved', 'probed', 'frozen'}:
                retained_count += 1

    status = summarize_status(seed_records, page_records, options.probe_only)
    source_manifest = {
        "source": source.to_dict(),
        "generated_at": seen_at,
        "seed_count": len(seed_urls),
        "candidate_count": len(candidates),
        "status": status,
        "seeds": seed_records,
        "pages": page_records,
    }
    result = {
        "id": source.id,
        "label": source.label,
        "weight": source.weight,
        "transport": source.transport,
        "authority_tier": source.authority_tier,
        "lane": source.lane,
        "seed_count": len(seed_urls),
        "candidate_count": len(candidates),
        "new_count": sum(1 for row in page_records if row.get("lifecycle_status") == "new"),
        "updated_count": sum(1 for row in page_records if row.get("lifecycle_status") == "updated"),
        "frozen_count": sum(1 for row in page_records if row.get("capture_status") == "frozen"),
        "ignored_count": sum(1 for row in page_records if row.get("capture_status") in {"filtered", "ignored"}),
        "status": status,
    }
    return result, source_manifest, catalog_updates


def run_crawl(options: CrawlOptions) -> dict[str, Any]:
    config = load_config(options.config_path)
    run_id = timestamp_id()
    seen_at = now_utc()
    run_dir = CRAWLER_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    fetcher = HttpFetcher(user_agent=config.user_agent, timeout=options.timeout)
    robots = RobotsManager(fetcher)
    page_catalog = load_page_catalog(PAGE_CATALOG_PATH)

    source_results: list[dict[str, Any]] = []
    all_page_snapshots: list[dict[str, Any]] = []
    all_catalog_updates: list[dict[str, Any]] = []

    for source in resolve_sources(config.sources, options):
        result, source_manifest, source_updates = process_source(source, options, fetcher, robots, page_catalog, run_id, seen_at)
        source_results.append(result)
        all_page_snapshots.extend(source_manifest["pages"])
        all_catalog_updates.extend(source_updates)
        write_json(run_dir / source.id / "manifest.json", source_manifest)
        print(
            f"[{result['status']}] {result['id']} seeds={result['seed_count']} candidates={result['candidate_count']} "
            f"new={result['new_count']} updated={result['updated_count']} frozen={result['frozen_count']} ignored={result['ignored_count']}"
        )

    run_manifest = {
        "generated_at": seen_at,
        "run_id": run_id,
        "run_dir": safe_relative(run_dir, CRAWLER_ROOT),
        "probe_only": options.probe_only,
        "refresh_existing": options.refresh_existing,
        "sources": source_results,
        "config_path": safe_relative(options.config_path, CRAWLER_ROOT),
        "version": config.version,
        "page_snapshot_count": len(all_page_snapshots),
    }
    write_json(run_dir / "run-manifest.json", run_manifest)
    write_jsonl(run_dir / "sources.jsonl", source_results)
    write_jsonl(run_dir / "page-snapshots.jsonl", all_page_snapshots)
    write_jsonl(
        run_dir / "new-or-updated.jsonl",
        [row for row in all_page_snapshots if row.get("lifecycle_status") in {"new", "updated"}],
    )
    (run_dir / "SUMMARY.md").write_text(render_summary(run_manifest), encoding="utf-8")

    state_dir = CRAWLER_ROOT / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    write_json(state_dir / "latest-run.json", run_manifest)
    write_json(state_dir / "source-health.json", {"generated_at": seen_at, "sources": source_results})
    write_json(PAGE_CATALOG_PATH, update_page_catalog(page_catalog, all_catalog_updates, run_id, seen_at))
    return run_manifest

# Data Branch Push Checklist

在首次真实推送 `data` 分支前，建议按以下顺序执行：

## 1. 本地测试
```bash
python3 crawler/run_tests.py
```

## 2. 校验 manual curated URL
```bash
python3 crawler/validate_manual_curated_urls.py
python3 crawler/probe_manual_curated_urls.py
```

## 3. 生成最新状态文件
```bash
python3 crawler/report_snapshots.py --limit 50 > crawler/state/catalog-report.md
python3 crawler/build_source_status_report.py > crawler/state/source-status-report.md
python3 crawler/build_manual_curated_backlog.py > crawler/state/manual-curated-backlog.md
python3 crawler/export_snapshot_relations.py
python3 crawler/build_data_branch_manifest.py
python3 crawler/audit_publish_bundle.py
python3 crawler/check_data_branch_readiness.py
```

## 4. 预览 latest-only 发布集合
```bash
python3 scripts/push_crawler_to_data_branch.py --branch data --remote origin --preview-only --latest-only
```

## 5. 框架总校验
```bash
python3 crawler/verify_framework.py
```

## 6. 首次真实推送
```bash
python3 scripts/push_crawler_to_data_branch.py --branch data --remote origin --latest-only
```

## 当前重点观察项
- `rogue_camp_163` 仍未补入 manual curated URL
- `data-branch-readiness.json` 中 `ready` 应为 `true`
- `preview_count` 不应为 0
- `required_files_present` 必须全部为 `true`

## Preflight Report

```bash
python3 crawler/build_preflight_report.py
```

用于把最新 run、snapshot relation 数量、manual curated probe 状态以及 readiness 结果汇总为 `crawler/state/preflight-report.json`。

## Data Branch Remote Probe

```bash
python3 crawler/probe_data_branch_remote.py
```

用于检查 `origin` 是否可访问，以及远端 `data` 分支是否已存在。首次真实推送前建议执行。

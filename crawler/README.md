# Diablo2 中文网页快照抓取框架

这个 `crawler/` 目录当前的职责非常明确：

> **定时发现新的高质量 Diablo2 中文文章，并在首次命中时保存网页快照；之后默认不再重复抓取同一篇静态文章。**

当前框架聚焦：
- 攻略
- 玩法
- FAQ
- 机制说明
- 地图 / 掉落 / 装备 / build 类文章

当前框架不聚焦：
- 交友
- 卖号
- 交易
- 估价
- 拍卖
- 灌水

## 核心原则

1. **优先保存快照，不急于深解析。**
2. **已抓到的静态文章默认冻结，不重复抓取。**
3. **维护 URL 与网页内容快照之间的稳定映射。**
4. **定时运行、过程尽量简洁、状态可追踪。**

## 当前产物

### 状态文件
- `crawler/state/latest-run.json`
- `crawler/state/source-health.json`
- `crawler/state/page_catalog.json`

### 快照文件
- `crawler/snapshots/<source_id>/*`

### 每次运行结果
- `crawler/runs/<run_id>/run-manifest.json`
- `crawler/runs/<run_id>/sources.jsonl`
- `crawler/runs/<run_id>/page-snapshots.jsonl`
- `crawler/runs/<run_id>/new-or-updated.jsonl`
- `crawler/runs/<run_id>/<source_id>/manifest.json`
- `crawler/runs/<run_id>/SUMMARY.md`

其中：
- `page_catalog.json` 是长期目录
- `page-snapshots.jsonl` 是单次运行产物
- `snapshot_path` 负责关联 URL 与保存下来的网页内容快照

## 运行方式

### 1. 日常探活
```bash
python3 crawler/run_snapshot.py --probe-only --limit-per-source 2
```

### 2. 日常定时抓取
```bash
python3 crawler/run_snapshot.py --limit-per-source 2
```

### 3. 指定来源抓取
```bash
python3 crawler/run_snapshot.py \
  --source 91d2 \
  --source diablo2_com_cn \
  --source ali213_d2r \
  --limit-per-source 2
```

### 4. 强制重抓已冻结页面
```bash
python3 crawler/run_snapshot.py --refresh-existing --source 91d2
```

### 5. 测试与校验
```bash
python3 crawler/run_tests.py
python3 crawler/verify_framework.py
```

## 关键机制

### 首次抓取后冻结
- 页面首次命中时：保存快照到 `crawler/snapshots/`
- 后续运行再次发现同一 URL：默认只记为 `frozen`，不重新抓正文
- 如确实需要重抓：使用 `--refresh-existing`

### 无关内容过滤
框架会按来源规则过滤：
- 交友
- 卖号
- 交易
- 估价
- 拍卖
- 部分视频/下载页

### URL 与快照关系
`crawler/state/page_catalog.json` 中每条记录会维护：
- `url`
- `title`
- `snapshot_id`
- `snapshot_path`
- `sha256`
- `capture_status`
- `first_seen_at`
- `last_seen_at`
- `last_run_id`

## 文档
- `crawler/SOURCE_OPTIONS.md`：来源选项清单
- `crawler/CRAWL_POLICY.md`：抓取准则与过滤策略
- `crawler/OPERATIONS.md`：日常运维与排障说明
- `.github/workflows/scheduler.yml`：GitHub Actions 定时抓取

## 快照索引查看

```bash
python3 crawler/report_snapshots.py --limit 20
python3 crawler/report_snapshots.py --source 91d2 --format json
```

## GitHub Actions 手动参数

workflow_dispatch 当前支持：
- `limit_per_source`
- `include_disabled`
- `refresh_existing`
- `probe_only`
- `source_ids`
- `commit_changes`

## Data Branch 发布

```bash
python3 scripts/push_crawler_to_data_branch.py --branch data --remote origin --run-id <run_id> --dry-run
```

GitHub Actions 会在非 `probe_only` 的情况下调用这个脚本，把 crawler 的快照结果发布到 `data` 分支。

## 快照清理

```bash
python3 crawler/prune_snapshots.py --keep-runs 10 --prune-snapshots --dry-run
```

用于清理旧 run 目录，以及删除 `page_catalog.json` 不再引用的孤儿快照文件。

### Workflow 清理参数
- `keep_runs`：保留最近多少次运行
- `prune_unreferenced_snapshots`：是否删除孤儿快照
- `prune_catalog_without_snapshots`：是否删除没有快照文件的噪音 catalog 记录

## 已验证静态目标

详见 `crawler/VERIFIED_SNAPSHOT_TARGETS.md`，用于记录已经验证过、适合长期冻结保存的静态攻略/玩法文章 URL。

## 来源状态报告

```bash
python3 crawler/build_source_status_report.py > crawler/state/source-status-report.md
```

输出每个来源的启用状态、可达性观察、已保存快照数量和最近运行状态。

## 手工补充静态页

对像 `rogue_camp_163`、巴哈、PTT、贴吧这类弱来源，可通过创建 `crawler/manual_curated_urls.json`（参考 `crawler/manual_curated_urls.example.json`）手工补 URL，配置加载时会自动合并到 `curated_urls`。

## Data Branch 预览

```bash
python3 scripts/push_crawler_to_data_branch.py --branch data --remote origin --preview-only
```

用于在首次真实推送前查看将发布到 `data` 分支的文件清单。

## 手工 curated 校验

```bash
python3 crawler/validate_manual_curated_urls.py
```

用于校验 `crawler/manual_curated_urls.json` 里的来源 ID、URL 格式和重复项，特别适合给 `rogue_camp_163` 这类弱来源补静态页时做预检查。

## Manual Curated Backlog

```bash
python3 crawler/build_manual_curated_backlog.py > crawler/state/manual-curated-backlog.md
```

用于标出当前仍然需要人工补种子的弱来源，例如 `rogue_camp_163`、TTBN、巴哈、PTT、贴吧。

## 手工 curated 管理

```bash
python3 crawler/manage_manual_curated_urls.py list
python3 crawler/manage_manual_curated_urls.py add --source rogue_camp_163 --url https://example.com/thread-1-1.html
python3 crawler/manage_manual_curated_urls.py remove --source rogue_camp_163 --url https://example.com/thread-1-1.html
```

用于持续维护 `crawler/manual_curated_urls.json`。

## 快照关系导出

```bash
python3 crawler/export_snapshot_relations.py
```

导出仅包含有效 `url -> snapshot_path` 关系的 `crawler/state/snapshot-relations.jsonl`，方便后续自定义转换链路直接消费。

## Data Branch 精简发布

```bash
python3 scripts/push_crawler_to_data_branch.py --branch data --remote origin --preview-only --latest-only
```

默认建议只把最新 `run_id` 对应的 `crawler/runs/<run_id>/` 连同 `state/`、`snapshots/` 和文档发布到 `data` 分支，避免历史 run 无限膨胀。

## 发布前审查

```bash
python3 crawler/audit_publish_bundle.py
```

用于在首次真实推送 `data` 分支之前，审查 latest-only 发布集合、关键状态文件和预览清单。

## Data Branch Ready Check

```bash
python3 crawler/check_data_branch_readiness.py
```

用于在首次真实推送 `data` 分支之前，检查 latest-only 发布审查、关键状态文件、workflow 发布设置以及弱来源 backlog 提示。

## 手工 curated 探测

```bash
python3 crawler/probe_manual_curated_urls.py
```

会尝试请求 `crawler/manual_curated_urls.json` 中的 URL，并输出状态、标题和错误信息到 `crawler/state/manual-curated-probe.json`，适合在正式接入弱来源前做快速探测。

## Data Branch Manifest

```bash
python3 crawler/build_data_branch_manifest.py
```

输出 latest-only data branch 发布清单到 `crawler/state/data-branch-manifest.json`，方便后续下游或审查工具直接消费。

## Manual Curated Playbook

详见 `crawler/MANUAL_CURATED_PLAYBOOK.md`，用于为 `rogue_camp_163`、TTBN、巴哈、PTT、贴吧等弱来源补静态页 URL。

## 首次真实推送清单

详见 `crawler/DATA_BRANCH_PUSH_CHECKLIST.md`，用于首次真实执行 `data` 分支推送前的操作检查。

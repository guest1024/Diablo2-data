# Crawler 运维手册

## 日常运行

### 建议频率
- 每日 1 次定时运行即可
- 对高频站点最多每日 2 次
- 不建议高频轮询详情页，因为已抓取页面默认冻结

### 标准命令
```bash
python3 crawler/run_snapshot.py --limit-per-source 2
```

## 重要状态文件

### 1. `crawler/state/page_catalog.json`
长期主目录。
查看：
- 哪些页面已保存快照
- 哪些页面被冻结
- 哪些页面被过滤为无关内容

### 1.1 `crawler/state/page-records/<source_id>/*.json`
逐网页层记录。
适合查看：
- 某个静态页是否已经首抓完成
- 某个页面文件是否发生过显式刷新
- data branch 中正文 HTML 旁边是否有对应详情 JSON
- 是否已经形成接近 wget mirror 的 host/path 层级

### 2. `crawler/state/source-health.json`
查看各来源最近一次：
- 是否可达
- 是否有新页面
- 是否只停留在 seed-only

### 3. `crawler/runs/<run_id>/new-or-updated.jsonl`
查看本次真正值得关注的新页面。

## 常见状态
- `saved`：本次已保存快照
- `probed`：仅探测，不保存快照
- `frozen`：已存在快照，本次跳过正文抓取
- `filtered`：命中无关内容过滤，不保存
- `ignored`：之前已被过滤，本次直接跳过

说明：
- `saved/frozen/ignored` 的静态页默认不重复抓正文
- 页面级记录文件只在首次抓取、过滤建档或显式刷新时更新
- 快照正文和详情 JSON 都按原始 host/path 目录输出，便于直接静态托管

## 异常处理

### 1. `seed-only`
说明种子页可达，但候选 URL 没筛出来。
处理方式：
- 调整 `discovery.include`
- 调整 `selection.preferred_keywords`
- 先不急着解析正文

### 2. `unreachable`
说明来源当前无法访问。
处理方式：
- 检查是否为出海问题
- 检查 robots / 证书 / 403
- 可先保留来源配置，后续用代理或人工导入

### 3. 误抓到无关页面
处理方式：
- 补 `relevance.exclude_title_keywords`
- 补 `relevance.exclude_url_keywords`
- 对论坛站改为更多 curated 白名单

## GitHub Actions
推荐直接使用：
- `.github/workflows/scheduler.yml`

默认行为：
- 定时触发
- 跑测试
- 跑抓取
- 提交 `crawler/` 内状态与快照更新
- 上传本次快照为 artifact

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

## 页面层逐文件导出

```bash
python3 crawler/export_page_records.py
```

把 `page_catalog.json` 拆成 `crawler/state/page-records/<source_id>/*.json`，用于给镜像正文补充详情索引。

## 镜像目录检查

推荐抽查：
- `crawler/snapshots/<source_id>/<host>/...`
- `crawler/state/page-records/<source_id>/<host>/...`

确认正文 HTML 与详情 JSON 是否都保留了原始 URL 层级。

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

## Page Catalog 分片导出

```bash
python3 crawler/export_page_catalog_partitions.py
```

将集中式 `page_catalog.json` 按来源拆分到 `crawler/state/page-catalog/<source_id>.jsonl`，同时保留索引文件。

## Workflow 稳定性脚本

为降低 YAML 多行 shell 出错概率，workflow 现在复用：
- `scripts/commit_crawler_metadata.py`
- `scripts/print_latest_run_id.py`

这比在 YAML 里内嵌长 heredoc 更稳定。

## 一键预检

```bash
python3 scripts/preflight_data_branch_push.py
```

用于在真实 data 分支推送前一次性跑测试、校验、探测、报告生成和 latest-only 发布预览。

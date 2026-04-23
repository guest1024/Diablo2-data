# Crawler Cleanup / Improvement Plan

## Scope
- `crawler/run_snapshot.py`
- `crawler/runner.py`
- `crawler/catalog.py`
- `crawler/models.py`
- `crawler/storage.py`
- `crawler/sources.zh.json`
- `crawler/README.md`
- `crawler/SOURCE_OPTIONS.md`
- `crawler/tests/*`
- `.github/workflows/*`
- `crawler/*.md`

## Goals
1. 把 crawler 明确收敛为“**定时发现新页面 + 首次抓取后冻结 + 保存网页快照与链接关系**”的框架。
2. 抓取目标聚焦静态攻略、玩法、FAQ、资料页；排除交友、卖号、交易、估价等无关内容。
3. 保持流程简洁：只维护来源、页面路径、页面标题、快照文件、生命周期状态。
4. 提供 GitHub Actions 定时执行方案与运维文档，降低维护成本。

## Smells / Risks To Remove
1. **重复抓取已冻结页面**：已经抓到的静态文章不应反复读取正文。
2. **链接与内容关系不明确**：需要稳定保存 `url -> snapshot_path -> metadata` 的映射。
3. **无关页面混入**：门户/论坛中的交易、视频、交友、卖号等内容需要过滤。
4. **缺少运维入口**：需要定时调度、执行说明与失败后排查文档。

## Planned Passes
1. 增加快照冻结机制与快照文件落盘。
2. 增加无关内容过滤与来源级规则字段。
3. 增加 GitHub workflow 与操作文档。
4. 补测试并跑一次真实小规模验证。

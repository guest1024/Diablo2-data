# Rogue Camp / 凯恩之角 手工补种子模板

当前 `rogue_camp_163` 在现环境下仍然是 `seed-only`，自动发现不到稳定帖子详情页。

## 建议补的内容类型
优先补 1~3 条长期有效的静态帖子 URL：
- 新手指引
- 开荒 / build / 配装
- 掉落 / 地图 / 机制说明
- FAQ / 联机教程

## 录入方式
假设你人工找到一个静态帖子：

```bash
python3 crawler/manage_manual_curated_urls.py add \
  --source rogue_camp_163 \
  --url https://bbs.d.163.com/thread-123456-1-1.html
```

然后执行：

```bash
python3 crawler/validate_manual_curated_urls.py
python3 crawler/probe_manual_curated_urls.py
python3 crawler/run_snapshot.py --source rogue_camp_163 --refresh-existing --limit-per-source 1
```

## 推荐筛选标准
- 标题是明显的攻略 / FAQ / 教程
- 页面是帖子详情页，不是列表页
- 不是交易、卖号、交友、水帖
- 尽量选择发布时间较早但仍长期有效的总结帖

## 当前状态
- 自动抓取入口：`https://bbs.d.163.com/forum-458-1.html`
- 当前问题：返回提示页，自动发现不到详情页
- 当前建议：手工 curated URL 作为唯一稳定接入方式

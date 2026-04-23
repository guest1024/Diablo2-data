# Manual Curated URL Playbook

当某个来源无法稳定从列表页自动发现帖子详情页时，使用本手册补充静态文章 URL。

## 标准流程

1. 用浏览器或搜索引擎找到目标静态攻略页 URL。
2. 执行：
   ```bash
   python3 crawler/manage_manual_curated_urls.py add --source <source_id> --url <url>
   ```
3. 校验：
   ```bash
   python3 crawler/validate_manual_curated_urls.py
   ```
4. 探测：
   ```bash
   python3 crawler/probe_manual_curated_urls.py
   ```
5. 重新抓取指定来源：
   ```bash
   python3 crawler/run_snapshot.py --source <source_id> --refresh-existing --limit-per-source 1
   ```

## 来源建议

### rogue_camp_163
- 目标：凯恩之角/罗格营地中的静态攻略帖、FAQ、职业玩法帖
- 优先找：
  - 新手指引
  - 职业 build
  - 地图/掉落/机制说明
- 当前问题：论坛入口页在现环境返回提示页，自动发现不到帖子详情链接

### ttbn_cn
- 目标：长期资料页、装备/地图/FAQ 页面
- 当前问题：连接重置，优先人工确认可访问文章页

### bahamut_d2r / ptt_diablo / tieba_*
- 目标：精华帖、FAQ、长期有效心得帖
- 当前问题：代理/403/出海限制
- 建议：只录入帖子详情页，不录入列表页

### news_blizzard_zh_tw
- 目标：繁中官方故事背景页、专题页
- 建议：优先录入 `article/<id>` 形式静态页面

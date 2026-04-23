# Manual Curated Backlog

Weak / blocked sources that likely need manual curated URL seeding are listed below.

| Source | Enabled | Transport | Saved snapshots | Manual curated count | Why it needs help | Suggested action |
| --- | --- | --- | ---: | ---: | --- | --- |
| rogue_camp_163 | True | direct | 0 | 0 | no saved snapshots yet; forum entry page still returns prompt/seed-only in current environment | 优先人工收集 1~3 条凯恩之角/罗格营地静态攻略帖 URL，再用 validate/probe 校验后写入 manual_curated_urls.json。 |
| news_blizzard_zh_tw | True | direct | 0 | 0 | no saved snapshots yet | 若需要补繁中官方故事/专题页，可直接手工加入 article URL。 |
| ttbn_cn | False | probe-only | 0 | 0 | no saved snapshots yet; transport=probe-only | 当前连接重置，建议先人工确认可访问页面，再补静态资料页 URL。 |
| bahamut_d2r | False | requires-proxy | 0 | 0 | no saved snapshots yet; transport=requires-proxy | 通过代理打开哈啦板后，挑选置顶/精华攻略帖 URL 手工录入。 |
| ptt_diablo | False | requires-proxy | 0 | 0 | no saved snapshots yet; transport=requires-proxy | 人工筛选高质量 M.*.A.html 文章，再加入 manual_curated_urls.json。 |
| tieba_d2r | False | manual-403 | 0 | 0 | no saved snapshots yet; transport=manual-403 | 人工从贴吧帖子页复制 /p/<id> 形式 URL，避免列表页 403。 |
| tieba_d2 | False | manual-403 | 0 | 0 | no saved snapshots yet; transport=manual-403 | 人工从贴吧帖子页复制 /p/<id> 形式 URL，避免列表页 403。 |

## Summary

- Sources currently needing manual curated attention: `7`
- Manual curated override file: `manual_curated_urls.json`


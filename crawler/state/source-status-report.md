# Source Status Report

- Version: `2026-04-23`
- Report path: `state/source-status-report.md`

| Source | Enabled | Region | Transport | Observed status | Saved snapshots | Manual curated | Capture summary | Lifecycle summary | Last run status | Notes |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| 91d2 | True | CN | direct | direct-ok | 1 | 0 | `{'frozen': 1}` | `{'frozen': 1}` | captured | 国内高价值资料站，适合作为长期主源之一。 |
| d2_blizzard_cn | True | CN | direct | direct-ok | 1 | 0 | `{'filtered': 1, 'frozen': 1}` | `{'ignored': 1, 'frozen': 1}` | captured | 官方中文入口，适合新闻、公告、术语层快照。 |
| diablo2_com_cn | True | CN | direct-http | http-ok-https-timeout | 1 | 0 | `{'frozen': 1}` | `{'frozen': 1}` | captured | 老牌中文资料库，HTTP 可达。 |
| bbs_diablo2_com_cn | True | CN | direct-http | http-ok-https-timeout | 1 | 0 | `{'filtered': 1, 'frozen': 1}` | `{'ignored': 1, 'frozen': 1}` | captured | 论坛只建议保留白名单精华帖。 |
| rogue_camp_163 | True | CN | direct | direct-ok | 0 | 0 | `{}` | `{}` | seed-only | 社区论坛入口，可后续补 curated 白名单。 |
| ali213_d2r | True | CN | direct | direct-ok | 1 | 0 | `{'frozen': 1}` | `{'frozen': 1}` | captured | 中文攻略聚合入口，适合补新手和流程向页面。 |
| gamersky_d2r | True | CN | direct | direct-ok | 4 | 0 | `{'saved': 3, 'frozen': 1}` | `{'unchanged': 1, 'new': 2, 'frozen': 1}` | captured | 攻略、新闻入口较稳定。 |
| 3dm_d2r | True | CN | direct | direct-ok-js-heavy | 4 | 0 | `{'frozen': 1, 'saved': 3}` | `{'frozen': 1, 'new': 3}` | captured | JS heavy guide hub; curated static攻略页已补齐。 |
| 17173_d2r | True | CN | direct | direct-ok | 4 | 0 | `{'saved': 3, 'frozen': 1}` | `{'unchanged': 1, 'frozen': 1, 'new': 2}` | captured | 中文新闻/攻略专区，可发现较多历史页面。 |
| news_blizzard_zh_tw | True | Overseas-ZH | direct | direct-ok | 0 | 0 | `{'ignored': 1}` | `{'ignored': 1}` | captured | 繁中官方新闻与背景故事页面。 |
| ttbn_cn | False | CN | probe-only | connection-reset | 0 | 0 | `{}` | `{}` | n/a | 候选优质资料站，但当前连接被重置。 |
| bahamut_d2r | False | Overseas-ZH | requires-proxy | outbound-blocked | 0 | 0 | `{}` | `{}` | n/a | 当前环境出海不可达，建议代理后启用。 |
| ptt_diablo | False | Overseas-ZH | requires-proxy | outbound-blocked | 0 | 0 | `{}` | `{}` | n/a | 当前环境出海不可达，建议代理后启用。 |
| tieba_d2r | False | CN | manual-403 | 403-forbidden | 0 | 0 | `{}` | `{}` | n/a | 直抓 403，可改为人工导出链接白名单。 |
| tieba_d2 | False | CN | manual-403 | 403-forbidden | 0 | 0 | `{}` | `{}` | n/a | 直抓 403，可改为人工导出链接白名单。 |

## Summary

- Configured sources: `15`
- Sources with saved snapshots: `8`
- Total saved snapshots: `17`
- Sources with manual curated overrides: `0`


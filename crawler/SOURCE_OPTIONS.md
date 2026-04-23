# Diablo2 中文站点选项清单

当前框架以“**网页路径快照**”为目标，优先保存高质量页面 URL、标题、状态与变更信息。

## 默认启用来源

1. **91D2 中文资料站**  
   https://www.91d2.cn/
2. **暴雪国服暗黑2中文站**  
   https://d2.blizzard.cn/
3. **CNBN 主站资料区**  
   http://www.diablo2.com.cn/
4. **CNBN 论坛精华白名单**  
   http://bbs.diablo2.com.cn/
5. **网易罗格营地论坛**  
   https://bbs.d.163.com/forum-458-1.html
6. **游侠网 D2R 攻略站**  
   https://gl.ali213.net/z/42565/
7. **游民星空 D2R 专区**  
   https://www.gamersky.com/z/dresurrected/
8. **3DM D2R 攻略页**  
   https://www.3dmgame.com/games/diablo2re/gl/
9. **17173 暗黑2重制版专区**  
   https://news.17173.com/z/ah2/
10. **暴雪新闻 zh-TW Diablo II**  
    https://news.blizzard.com/zh-tw/diablo2

## 已纳入配置、默认禁用来源

11. **TTBN 资料站**  
    https://www.ttbn.cn/
12. **巴哈姆特 D2R 哈啦板**  
    https://forum.gamer.com.tw/B.php?bsn=742
13. **PTT DIABLO 板**  
    https://www.ptt.cc/bbs/DIABLO/index.html
14. **百度贴吧：暗黑2重制版吧**  
    https://tieba.baidu.com/f?kw=%E6%9A%97%E9%BB%912%E9%87%8D%E5%88%B6%E7%89%88
15. **百度贴吧：暗黑破坏神2吧**  
    https://tieba.baidu.com/f?kw=%E6%9A%97%E9%BB%91%E7%A0%B4%E5%9D%8F%E7%A5%9E2

## 使用建议

- 国内高权重站点默认启用。
- 海外中文站与出海受限站点保留配置，后续可走代理或人工导入路径。
- 论坛站点只建议沉淀“页面路径快照”，后续正文转换由你们自定义。

## 已验证静态目标

详见 `crawler/VERIFIED_SNAPSHOT_TARGETS.md`，用于记录已经验证过、适合长期冻结保存的静态攻略/玩法文章 URL。

## 来源状态报告

```bash
python3 crawler/build_source_status_report.py > crawler/state/source-status-report.md
```

输出每个来源的启用状态、可达性观察、已保存快照数量和最近运行状态。

## 手工补充静态页

对像 `rogue_camp_163`、巴哈、PTT、贴吧这类弱来源，可通过创建 `crawler/manual_curated_urls.json`（参考 `crawler/manual_curated_urls.example.json`）手工补 URL，配置加载时会自动合并到 `curated_urls`。

## Manual Curated Backlog

```bash
python3 crawler/build_manual_curated_backlog.py > crawler/state/manual-curated-backlog.md
```

用于标出当前仍然需要人工补种子的弱来源，例如 `rogue_camp_163`、TTBN、巴哈、PTT、贴吧。

## Manual Curated Playbook

详见 `crawler/MANUAL_CURATED_PLAYBOOK.md`，用于为 `rogue_camp_163`、TTBN、巴哈、PTT、贴吧等弱来源补静态页 URL。

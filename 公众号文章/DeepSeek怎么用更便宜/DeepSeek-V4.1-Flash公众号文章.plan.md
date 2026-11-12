---
name: DeepSeek 怎么用更便宜 · 公众号短文（闲时官方 / 峰时 Cloudflare）
overview: 产出 500 字内公众号短文 + 封面 + 峰时切换信息图，全部落在独立文件夹内
status: draft
todos:
- MARK[id: p0-data, status: completed, content: "阶段0 数据：只读复核生产站 ModelInfo/ModelPeakPricing，官方闲时 0.02/1/4、峰时 0.04/2/8、Cloudflare 0.024/0.80/4.8，Cloudflare 无峰谷"]
- MARK[id: p1-draft, status: completed, content: "阶段1 文稿：改为「闲时用官方、峰时用 Cloudflare」单一主张，正文 421 字"]
- MARK[id: p2-images, status: completed, content: "阶段2 配图：复用封面；新做信息图（价格表 + 决策条 + 三柱对比），数值右对齐无溢出"]
- MARK[id: p3-review, status: completed, content: "阶段3 复核：脚本复算 0.86/0.95/1.73 分、峰时省 44.9%、闲时溢价 10.2%、组合省 29.9%，与文中约数一致；正文 412 字"]
- MARK[id: p4-report, status: completed, content: "阶段4 交付：文稿 + 素材 + 计划书 + 封面（复用）+ 峰时切换信息图"]
session_id: 0299924c
---

# DeepSeek 省钱组合 · 公众号短文 计划书

## 约束

- **唯一交付目录**：`D:/work/zhilingdoc/公众号文章/DeepSeek怎么用更便宜/`。
- **篇幅**：正文 ≤ 500 字（不含参考信息与话题标签）；比上一版更短、更直观。
- **单一主张**：只讲一件事——闲时用官方、峰时用 Cloudflare；不铺开讲缓存、输出、其它渠道。
- **范围**：只讨论 DeepSeek V4.1 Flash 与同代 Cloudflare 渠道，不写 Pro。
- **事实红线**：价格与单次费用全部来自站内数据库或按站内计价公式复算；不承诺缓存命中率。

## 数据口径

- 生产站 `ModelInfo` / `ModelPeakPricing`，2026-11-02 只读复核。
- 单次示例按站内 Flash 平均 token 结构：输入 125,071、缓存命中 98.35%、输出 966；含 3% 转发费率。
- 组合收益按「峰时占一半」的假设粗算，文中已注明是假设。

## 核心结论

1. **闲时官方最便宜**：0.86 分/次；Cloudflare 0.95 分，贵约 10%。
2. **峰时 Cloudflare 最便宜**：0.95 分 vs 官方峰时 1.73 分，省 45%。
3. **组合后任何时段不超过 1 分**：把峰时拉回接近闲时的水平。
4. **不要一直用 Cloudflare**：它没有峰时，但每一项都比官方闲时贵一点。

## 实施步骤

- MARK[id: p0-data, status: completed, content: "阶段0 数据：只读复核生产站 ModelInfo/ModelPeakPricing，官方闲时 0.02/1/4、峰时 0.04/2/8、Cloudflare 0.024/0.80/4.8，Cloudflare 无峰谷"]
  - 复核三套价格与峰谷配置；确认 Cloudflare 条目对客启用（`enabled_in_agent=True`）。
  - 数据固化到 `实测素材.md`。
- MARK[id: p1-draft, status: completed, content: "阶段1 文稿：改为「闲时用官方、峰时用 Cloudflare」单一主张，正文 421 字"]
  - 结构：一句话结论 → 价格表 → 算账 → 为什么不一直用 Cloudflare → 怎么切 → 一句总结。
- MARK[id: p2-images, status: completed, content: "阶段2 配图：复用封面；新做信息图（价格表 + 决策条 + 三柱对比），数值右对齐无溢出"]
  - `images/封面-DeepSeek省钱.png`（复用）；`images/DeepSeek-峰时切换方案.png`（新做，SVG 源同目录）。
- MARK[id: p3-review, status: completed, content: "阶段3 复核：脚本复算 0.86/0.95/1.73 分、峰时省 44.9%、闲时溢价 10.2%、组合省 29.9%，与文中约数一致；正文 412 字"]
  - 复算单次费用、降幅、溢价与组合收益；检查字数、图片引用、口径一致性。
- MARK[id: p4-report, status: completed, content: "阶段4 交付：文稿 + 素材 + 计划书 + 封面（复用）+ 峰时切换信息图"]

## 风险提示

| 风险 | 说明 | 回退策略 |
| --- | --- | --- |
| 生产峰谷时区未同步 | 生产站 `TIME_ZONE=UTC`，实际高峰为北京时间 17:00–20:00、22:00–02:00，与定价页文案 09:00–12:00、14:00–18:00 不一致 | 发布前完成生产同步；否则删除具体时段，改为「以模型价格页标注为准」 |
| 组合收益依赖假设 | 「一天一半时间在峰时」是演示假设，非实测分布 | 文中明确写「一天有一半时间在峰时的话」 |
| 缓存命中不可承诺 | 上游缓存策略、前缀稳定性都会影响命中 | 表述为「按站内近 30 天平均结构」，不写「一定命中」 |
| 价格调整 | 上游价格可能变动 | 文中注明「以模型价格页标注为准」，参考信息给出官方价格页 |

## 验收标准

- 正文 ≤ 500 字。
- 只出现 DeepSeek V4.1 Flash 与 Cloudflare 渠道，不出现 Pro、不展开其它渠道。
- 所有数字可由 `实测素材.md` 复算。
- 图片引用路径可解析，信息图无文字溢出、无遮挡。

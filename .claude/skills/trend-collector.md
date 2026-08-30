---
name: trend-collector
description: 获取最新 AI 行业趋势，更新 static/data/trends.json
type: skill
---

# AI 行业趋势采集 Skill

> **调度状态（2026-08-29 更新）**：原"每周三 9:17 自动运行（session 内需激活）"机制已失效——依赖本地会话开启，导致数据停在 2026-06-02。
> 现行机制：ZCode 定时自动化（每周三 9:30），**尚待创建**——因"定时任务会话内不能创建新定时任务"的系统限制，需在普通会话中创建。
> 创建提示词已固化在下方第 0 节，新会话照抄执行 `CronCreate` 即可。
>
> 2026-08-29 已人工补跑一次：trends.json 30→49 条，data_period 至 2026.08，trends.tsx 时间文案改为动态读取 data_period。

## 1.5 第 1 信息源：follow-builders 建造者 feed（2026-08-30 接入）

借鉴 [zarazhangrui/follow-builders](https://github.com/zarazhangrui/follow-builders) 的思路——**顶级建造者一手动态是趋势的最上游信号**（领先媒体报道数天）。该项目用 GitHub Actions 每日抓取 8+ 位建造者的 X 动态、官方博客、AI 播客（含转录），feed JSON 直接存在其仓库里，**raw 一次 HTTP 拉取即可，无需安装任何依赖**：

| Feed | 覆盖窗口 | 结构 |
|---|---|---|
| `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json` | 24h | `d.x[]` → `name/handle/bio` + `tweets[].text/createdAt`；`d.stats` |
| `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-blogs.json` | 72h | `d.blogs[]`（发文频率低，常为空，属正常） |
| `https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-podcasts.json` | 14d | `d.podcasts[]` → `title/publishedAt`（含转录） |

**采集流程中的用法**：
1. 每周采集开始时先 curl 拉取三个 feed；**拉取失败或为空直接跳过，回退 WebSearch 流程，不阻塞**
2. 从推文/播客/博客中识别"有行业信号"的内容（模型动向、价格与商业模式、Agent 生态、基础设施），**重大信息需 WebSearch 交叉验证后入库**；单条推文一般只够 B/C 级，不硬凑 S/A
3. 与已有趋势按 title 去重
4. 各建造者的完整信息源清单见其仓库 `config/default-sources.json`，可按需扩展

2026-08-30 首次接入演示：从 feed-x 提取 2 条 B 级行业信号入库（token 价格上涨预判、前沿实验室押注 RSI）。

## 0. 定时任务创建提示词（待执行）

在普通（非定时任务）会话中用 CronCreate 创建：cron `30 9 * * 3`，recurring=true，title「每周三 9:30 采集 AI 行业趋势并自动部署」，prompt 如下：

```
执行 FDE 学习中心的 AI 行业趋势每周采集任务（项目即当前工作区）：

1. 读取 static/data/trends.json，收集所有已有趋势的 title 用于去重，当前 data_period 与 last_updated。
2. 先拉取 follow-builders 建造者 feed（curl 本文第 1.5 节的三个 raw URL，拉取失败直接跳过不阻塞），从建造者推文/播客/博客中识别有行业信号的内容，重大信息用联网搜索交叉验证后入库。
3. 用联网搜索采集近一周（重点是上周至今）的 AI 行业动态，覆盖 6 大类别：模型发布、研究论文、开源项目、行业动态（投融资/政策/市场）、推理部署（推理引擎/硬件/部署方案）、Agent 应用（框架/协议/产品化）。每类至少 1-2 条，只收录有可靠来源的重磅信息。
4. 新趋势条目字段：title、summary（2-3 句）、source、url、date（YYYY-MM-DD）、category、impact_level（S/A/B/C）、fde_relevance。
5. 按 title 去重后追加进 trends.json 对应 category 的 trends 数组（旧条目全部保留）。
6. 更新 trends.json：last_updated=今天、total_trends 重算、data_period 的结束月份顺延、highlights 两组（S 级亮点 / A 级速览）用最新重要条目刷新。
7. 若 GitHub Trending 出现值得收录的重量级新 AI 项目，追加到 src/pages/github-trends.tsx 对应分组的 repos 数组（字段：name、stars、growth、description、category、url、source、date、highlight 可选），注意与已有项目去重。
8. git add 相关文件并 commit（提交说明"更新 AI 趋势数据 YYYY-MM-DD"），然后 git push origin master。
9. 输出简报：本次新增趋势数、各类别条数、GitHub 新增项目数、git 推送结果。

注意：单次搜索失败就跳过该来源继续；不修改本任务范围外的任何文件；git 可免交互推送（连接被重置时等待重试几次）。
```

## 用途

采集 AI 领域最新行业动态，更新 `static/data/trends.json`，为 `src/pages/trends.tsx` 页面提供数据。

## 采集范围

### 趋势类别 + 搜索关键词

| 类别 | 关键词 |
|------|--------|
| 模型发布 | LLM release, new model, GPT, Claude, Gemini, Llama, Qwen, 大模型发布 |
| 研究论文 | arXiv LLM, Transformer, attention, reasoning model, paper breakthrough |
| 开源项目 | open source LLM, AI framework, inference engine, GitHub trending AI |
| 行业动态 | AI funding, startup, acquisition, regulation, policy, AI company |
| 推理与部署 | inference optimization, vLLM, TensorRT, quantization, GPU, serving |
| Agent 与应用 | AI agent, autonomous agent, multi-agent, RAG, MCP, AI application |

### 数据源

通过 WebSearch 搜索获取（按优先级）：
1. **arXiv** — `site:arxiv.org "LLM" OR "Transformer" 2026`
2. **GitHub Trending** — WebSearch 搜索 `GitHub trending AI LLM 2026`
3. **Hacker News** — `site:news.ycombinator.com AI LLM 2026`
4. **Twitter/X** — WebSearch 搜索 `AI news LLM breakthrough 2026`
5. **科技媒体** — TechCrunch、The Verge、36Kr 等关于 AI 的最新报道
6. **官方博客** — OpenAI Blog、Anthropic Blog、Google AI Blog、Meta AI Blog 等

## 采集流程

1. **读取现有数据**：先 `Read` 当前 `static/data/trends.json`，提取已有趋势 URL 列表，用于去重
2. **逐类别搜索**：对每个类别，用 2-3 个核心关键词 + WebSearch 搜索（限定近 30 天内容）
3. **提取信息**：从搜索结果中提取 title, source, url, date, category, summary, impact
4. **分级评估**：对每条趋势进行 impact_level 评估（S/A/B/C 四级）
5. **去重合并**：按 URL 去重，保留新趋势
6. **更新文件**：写入 `static/data/trends.json`，更新 `last_updated` 和 `total_trends`

## 数据格式

每个趋势对象：
```json
{
  "title": "趋势标题",
  "source": "来源（如 arXiv / GitHub / OpenAI Blog / TechCrunch 等）",
  "url": "原始链接",
  "date": "发布日期 YYYY-MM-DD",
  "category": "模型发布/研究论文/开源项目/行业动态/推理部署/Agent应用",
  "summary": "一句话摘要（中文）",
  "impact_level": "S/A/B/C",
  "fde_relevance": "对 FDE 岗位的相关性说明（中文，1-2 句话）"
}
```

影响级别说明：
- **S**：重大突破（如新模型架构、范式转变、里程碑发布）
- **A**：重要进展（如主流模型大版本更新、重要论文、关键工具发布）
- **B**：值得关注（如新项目起步阶段、行业分析、性能优化）
- **C**：参考信息（如社区讨论、小更新、观点文章）

整个 JSON 结构：
```json
{
  "last_updated": "YYYY-MM-DD",
  "total_trends": 数字,
  "categories": [
    {
      "name": "模型发布",
      "trends": [趋势对象...]
    },
    ...
  ],
  "highlights": [
    {
      "title": "本周亮点",
      "items": ["亮点1", "亮点2", ...]
    }
  ]
}
```

## 采集策略

- 每类至少采集 3-5 条新趋势（如有）
- 优先选择权威来源（官方博客、顶级会议论文、高星开源项目）
- 保留已有数据中的老趋势（不完全替换，而是增量更新，最多保留每个类别 20 条）
- 老趋势如果超过 90 天且无新进展，标记为 `archived: true`
- 每条趋势必须包含 `fde_relevance` 字段，说明对 FDE 学习/面试的意义

## 输出报告

采集完成后，输出简要报告：
- 本次新增趋势数
- 各类别趋势数
- 新增 S 级/A 级趋势列表
- 被归档的老趋势数

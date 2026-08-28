# FDE Website - Claude Code 配置

## Skills

### 岗位采集 (/job-collector)

定期采集 FDE 相关岗位，更新 `static/data/jobs.json`。

- **Skill 定义**: `.claude/skills/job-collector.md`
- **采集脚本**: `scripts/collect_jobs.py`（兜底用，产出质量低；实际采集由 AI 联网搜索完成）
- **数据文件**: `static/data/jobs.json`
- **调度**: **ZCode 定时自动化**（automation-96a1351a，每周一 9:30）自动执行采集 → 更新 json → git push → Cloudflare Pages 自动部署；触发时需本机开机且 ZCode 运行
- **2026-08-28 变更**：jobs.tsx 页面已支持 `first_seen` 字段（新增岗位自动统计"近两周新增"）、数据新鲜度警示（>30 天未更新显示警示条）、热门技能按 tags 出现次数自动统计

采集 6 大类别岗位：大模型推理/部署、大模型应用/Agent、大模型算法/架构、AI 平台/基础设施、AI 解决方案/架构、AI 前沿部署工程师

### AI 行业趋势采集 (/trend-collector)

定期采集 AI 行业动态，更新 `static/data/trends.json`。

- **Skill 定义**: `.claude/skills/trend-collector.md`
- **数据文件**: `static/data/trends.json`
- **展示页面**: `src/pages/trends.tsx`
- **调度**: 每周三 9:17 AM 自动运行（Claude session 内需激活）

采集 6 大类别趋势：模型发布、研究论文、开源项目、行业动态、推理部署、Agent 应用。

## 项目结构

```
docs/                 # 系统学习（主站内容）
docs-opensource/      # 开源项目解读
docs-agentic-ai/      # Agentic AI 系统学习
docs-tools/           # 工具教程
src/pages/jobs.tsx    # 招聘动态页面
static/data/jobs.json # 招聘数据
```

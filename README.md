# FDE 学习中心

> **AI 前沿部署工程师（Frontier Deployment Engineer）—— 从入门到面试的系统性学习平台**

<p align="center">
  <a href="https://fde-academy.pages.dev/"><strong>在线阅读</strong></a> ·
  <a href="#-平台模块"><strong>平台模块</strong></a> ·
  <a href="#-本地运行"><strong>本地运行</strong></a>
</p>

---

## 概述

FDE 学习中心是一个面向 **AI 前沿部署工程师** 的系统性学习平台，覆盖从 AI 基础理论到生产部署的全栈能力。内容持续更新，免费开放。

### 平台模块

| 模块 | 路由 | 内容 | 适合人群 |
|------|------|------|----------|
| FDE 系统学习 | [/](https://fde-academy.pages.dev/) | 15 个阶段：AI 基础 → GPU → 推理引擎 → 分布式 → 生产部署 | AI 解决方案架构师 |
| Agentic AI 系统学习 | [/agentic-ai/](https://fde-academy.pages.dev/agentic-ai/) | 20 篇：Python 基础 → LLM → LangGraph → RAG → 多智能体 → 实战 | AI Agent 工程师 / 校招 / 实习生 |
| 开源源码解读 | [/opensource/](https://fde-academy.pages.dev/opensource/) | 6 个项目：nanoGPT、llm.c、llama.cpp、vLLM、SGLang、Claude Code | 深入理解底层原理 |
| 工具教程 | [/tools/](https://fde-academy.pages.dev/tools/) | Cursor、Claude Code、Karpathy AI 编程、OpenSpec 工作流 | 提升开发效率 |
| AI 行业趋势 | [/trends/](https://fde-academy.pages.dev/trends/) | 30+ 条动态，S/A/B/C 四级影响评估，每周更新 | 把握行业方向 |
| GitHub 趋势 | [/github-trends/](https://fde-academy.pages.dev/github-trends/) | 半年数据，5 大分类 31 个项目 | 追踪开源前沿 |
| AI 应用趋势 | [/ai-applications/](https://fde-academy.pages.dev/ai-applications/) | 40+ 新兴产品，从大厂到独立开发者 | 发现机会与创新 |
| FDE 招聘动态 | [/jobs/](https://fde-academy.pages.dev/jobs/) | 5 大类别：推理/部署、Agent、算法/架构、平台/基础设施、解决方案 | 求职与招聘参考 |

---

## 页面预览

### 首页

![首页](static/screenshots/home-dashboard.png)

### FDE 系统学习 — 什么是 FDE

![系统学习](static/screenshots/learn-doc.png)

### Agentic AI 系统学习 — Python 工程基础

![Agentic AI](static/screenshots/agentic-ai-doc.png)

### GitHub AI 趋势（半年数据）

![GitHub 趋势](static/screenshots/github-trends.png)

### AI 应用趋势（40+ 新兴产品）

![AI 应用趋势](static/screenshots/ai-applications.png)

---

## 内容涵盖

- **AI 基础理论**：Transformer、模型训练、GPU 架构、推理优化
- **生产部署实战**：vLLM/SGLang 推理引擎、K8s 部署、可观测性、成本优化
- **Agentic AI**：LangGraph、RAG、多智能体编排、MCP/A2A 协议
- **源码解读**：nanoGPT、llm.c、llama.cpp、vLLM、SGLang、Claude Code 架构
- **面试与招聘**：面试答题框架、技能知识图谱、真实岗位列表
- **行业动态**：AI 趋势、GitHub 热门项目、新兴 AI 产品

---

## 本地运行

```bash
npm install
npm start
```

打开 [http://localhost:3000](http://localhost:3000) 即可查看（也可直接双击项目根目录的 `FDE一键启动.exe`）。

## 部署

站点部署在 **Cloudflare Pages**，连接 GitHub 仓库后全自动：

- `git push origin master` → 自动构建（`npm run build`）→ 自动发布到生产域名
- 推送其他分支 → 自动生成 `<分支名>.fde-academy.pages.dev` 预览链接，不影响线上
- 绑定自定义域名：Cloudflare Pages 控制台 → Custom domains，域名 DNS 添加 CNAME 指向 `fde-academy.pages.dev`，并把 `docusaurus.config.js` 里的 `url` 改成自定义域名

## 贡献

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交修改：`git commit -m '描述你的改动'`
4. 推送并提 Pull Request

## License

MIT

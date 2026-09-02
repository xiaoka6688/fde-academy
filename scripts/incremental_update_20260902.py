#!/usr/bin/env python3
"""增量更新 jobs.json 和 trends.json — 2026-09-02 采集"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
JOBS_FILE = ROOT / "static" / "data" / "jobs.json"
TRENDS_FILE = ROOT / "static" / "data" / "trends.json"

# ============ 新增岗位（2026-09-01 ~ 09-02 采集） ============
NEW_JOBS = {
    "大模型推理/部署": [
        {
            "title": "大模型推理框架研发工程师",
            "company": "腾讯",
            "location": "杭州",
            "url": "https://refund.zhipin.com/job_detail/5df1bedbc67ea5750nB93Nu8GFpQ.html",
            "source": "BOSS直聘",
            "tags": ["vLLM", "SGLang", "TensorRT-LLM", "分布式推理", "异构芯片"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "AI推理引擎开发工程师（端侧推理加速）",
            "company": "某大型知名互联网公司",
            "location": "全国",
            "url": "https://www.zhipin.com/job_detail/30250949fbbd082f0nB-2tm0FFJZ.html",
            "source": "BOSS直聘",
            "tags": ["端侧推理", "量化", "算子加速", "投机采样", "CUDA", "vLLM"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "大模型推理性能优化算法工程师",
            "company": "京东科技集团",
            "location": "北京",
            "url": "https://m.liepin.com/job/1979256549.shtml",
            "source": "猎聘",
            "tags": ["vLLM", "SGLang", "TensorRT-LLM", "推理优化", "多模态"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "AI infra 推理框架开发工程师",
            "company": "寒武纪",
            "location": "全国",
            "url": "https://m.zhipin.com/job_detail/f227f0ebcaa94e510nVy3di0EFJR.html",
            "source": "BOSS直聘",
            "tags": ["分布式推理", "LLM", "Diffusion", "异构硬件", "性能优化"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "AI推理部署工程师（具身智能方向）",
            "company": "辉羲智能",
            "location": "上海",
            "url": "https://www.liepin.com/s/ycsfaijgssnjau6td/",
            "source": "猎聘",
            "tags": ["具身智能", "推理部署", "边缘推理", "实时推理"],
            "salary": "30-50K·15薪",
            "first_seen": "2026-09-02",
        },
        {
            "title": "大模型算法工程师",
            "company": "汇川技术",
            "location": "深圳",
            "url": "https://m.jobui.com/company/1261638/salary/j/damoxingsuanfagongchengshi/",
            "source": "职友集",
            "tags": ["LLM", "vLLM", "XInference", "llama.cpp", "NLP", "工业智能"],
            "salary": "面议",
            "first_seen": "2026-09-02",
        },
    ],
    "大模型应用/Agent": [
        {
            "title": "AI Agent工程师（CSAS团队）",
            "company": "联想弘扬",
            "location": "全国",
            "url": "https://refund.zhipin.com/job_detail/2a0a0458b44058db0nF70t6-GFZY.html",
            "source": "BOSS直聘",
            "tags": ["AI Agent", "MCP", "LangGraph", "Skills", "平台架构", "0到1"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "端侧智能体工程师",
            "company": "某大型行业公司",
            "location": "深圳",
            "url": "https://m.zhipin.com/job_detail/8a3bc7081536661c0nB90tS9F1dW.html",
            "source": "BOSS直聘",
            "tags": ["端侧Agent", "端云协同推理", "LangGraph", "工具调用", "多模态", "语音Agent"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "AI Agent开发工程师",
            "company": "杭州某科技公司",
            "location": "杭州",
            "url": "https://msearch.51job.com/jobs/hangzhou-xsq/173165516.html",
            "source": "前程无忧",
            "tags": ["LangChain", "LangGraph", "AutoGen", "CrewAI", "RAG", "智能客服", "工作流"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "AI平台研发工程师（AI Agent Infra）",
            "company": "网易游戏",
            "location": "广州",
            "url": "https://hr.game.163.com/recruit.html?cityStr=%E5%B9%BF%E5%B7%9E",
            "source": "网易招聘",
            "tags": ["Agent Infra", "Agent编排", "工具管理", "记忆管理", "安全治理", "平台化"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
        {
            "title": "AI Agent开发工程师",
            "company": "滴滴",
            "location": "北京",
            "url": "https://talent.didiglobal.com/social/p/62193",
            "source": "滴滴招聘",
            "tags": ["LangChain", "LangGraph", "CrewAI", "Dify", "二次开发", "并发控制", "资源隔离"],
            "salary": "面议",
            "first_seen": "2026-09-01",
        },
    ],
}

# ============ 新增趋势（2026-08-31 ~ 09-02 采集） ============
NEW_TRENDS = {
    "模型发布": [
        {
            "title": "Anthropic 发布 Fable 5.1：Agent 长时运行 + 成本最高降 45%",
            "source": "Anthropic / 华尔街日报",
            "url": "https://www.anthropic.com/news",
            "date": "2026-09-01",
            "category": "模型发布",
            "summary": "Anthropic 发布新一代旗舰模型 Fable 5.1，同时推出 Mythos 5.1。重点优化 Agent 连续运行数小时的能力，支持自主规划步骤、多工具调用、出错后继续执行。API 定价输入 $10/M token、输出 $50/M token，典型任务成本降低 25%，工具调用频繁的 Agent 任务成本最高降低 45%。",
            "impact_level": "A",
            "fde_relevance": "Agent 长时运行能力直接影响 Agent 服务的推理编排和成本模型；45% 成本降幅验证了工具调用优化的工程价值。",
        },
        {
            "title": "谷歌 Gemini 3.8 Flash 即将上线：编程能力追赶 OpenAI/Anthropic",
            "source": "华尔街日报 / IT之家",
            "url": "https://m.weibo.cn/detail/5338639593639953",
            "date": "2026-09-02",
            "category": "模型发布",
            "summary": "据华尔街日报报道，谷歌即将发布 Gemini 3.8 Flash（内部代号 Skimaki），最早当地时间周三上线，主打编程能力大幅升级，追赶 OpenAI 与 Anthropic。",
            "impact_level": "B",
            "fde_relevance": "Flash 系列主打低延迟高吞吐，新版本可能改变推理服务的模型选型性价比。",
        },
        {
            "title": "NVIDIA 发布 Nemotron-Nano-9B-v2：可切换推理模式的端侧小模型",
            "source": "NVIDIA / AI D-A-M-N",
            "url": "https://ai-damn.com/nvidia-unveils-nemotron-nano-9b-v2-with-switchable-ai-reasoning-1756767980365",
            "date": "2026-09-01",
            "category": "模型发布",
            "summary": "NVIDIA 推出 Nemotron-Nano-9B-v2 小语言模型，主打效率和灵活性，支持可切换的 AI 推理模式，面向资源受限场景。",
            "impact_level": "C",
            "fde_relevance": "端侧小模型是推理部署的重要分支，可切换推理模式为动态算力分配提供新思路。",
        },
        {
            "title": "星火 X2.5-4B/1.7B 开源：端侧唯一百万上下文 + 昇腾原生支持",
            "source": "科大讯飞 / 华为计算",
            "url": "http://m.toutiao.com/group/7680565083054948879/",
            "date": "2026-09-01",
            "category": "模型发布",
            "summary": "科大讯飞词元星火推出并开源星火 X2.5-4B 和 X2.5-1.7B 两款端侧通用大模型，是端侧模型中唯一原生支持最长 100 万 Token 上下文的模型。昇腾 AI 基础软硬件为两款模型提供原生训练推理全流程支持。",
            "impact_level": "B",
            "fde_relevance": "端侧百万上下文 + 昇腾原生支持，为信创端侧部署提供新选项；百万上下文对端侧 KV Cache 管理提出新挑战。",
        },
    ],
    "推理部署": [
        {
            "title": "vLLM 安全修复 + AutoRound block-wise FP8 支持",
            "source": "vLLM GitHub / repojournal",
            "url": "https://repojournal.com/showcase/local-llm/2026-09-01/vllm-bounds-validation-errors-autoround-fp8-arrives",
            "date": "2026-09-01",
            "category": "推理部署",
            "summary": "vLLM 发布安全修复：限制 validation-error 响应体大小，防止潜在 DoS 攻击。同时新增 AutoRound 格式的 block-wise FP8 支持，实现量化感知推理。同期 llama.cpp 和 SGLang 推送了 Blackwell 和 ROCm 的 kernel 融合优化。",
            "impact_level": "B",
            "fde_relevance": "推理服务安全修复需及时跟进升级；AutoRound FP8 为量化推理提供新格式支持；Blackwell/ROCm kernel 融合影响硬件选型和性能调优。",
        },
        {
            "title": "Vercel AI Gateway 新增 per-user 预算：token 成本治理基础设施化",
            "source": "X @rauchg (Vercel CEO) · follow-builders feed",
            "url": "https://x.com/rauchg/status/2094523399280435630",
            "date": "2026-08-31",
            "category": "推理部署",
            "summary": "Vercel CEO Guillermo Rauch 指出：coding token 已成为基础设施，但多数企业仍用临时方式采购管理，缺乏容量规划与成本治理。Vercel AI Gateway 推出 per-key 和 per-user 预算功能，类比 AWS 密钥治理来管理 AI token 消耗。",
            "impact_level": "B",
            "fde_relevance": "token 成本治理正成为企业 AI 基础设施标准议题，对应 FDE 成本运营章节的实际落地需求。",
        },
    ],
    "行业动态": [
        {
            "title": "Box CEO：开源权重模型逼近企业级拐点，自训练模型门槛骤降",
            "source": "X @levie (Box CEO) · follow-builders feed",
            "url": "https://x.com/levie/status/2094650992818274514",
            "date": "2026-09-01",
            "category": "行业动态",
            "summary": "Box CEO Aaron Levie：开源权重基础模型能力快速提升、后训练基础设施日益成熟商业化，拥有大量数据的企业现在可以合理地训练自己的模型，无需在研究层面与前沿实验室竞争。通用前沿模型仍在广泛任务上领先，但垂直领域模型数量将大幅增长。",
            "impact_level": "B",
            "fde_relevance": "企业自部署+微调需求上升，正是 FDE 岗位的核心场景扩张；后训练基础设施成熟降低了部署门槛。",
        },
        {
            "title": "AI 3D 世界生成竞赛升温：影眸 Hyper3D + VAST 30 亿融资",
            "source": "每日经济新闻",
            "url": "http://m.toutiao.com/group/7680604065528660530/",
            "date": "2026-09-01",
            "category": "行业动态",
            "summary": "影眸科技发布世界生成模型 Hyper3D WorldGen，上传场景图片即可自动生成独立 3D 资产。同日 3D 大模型公司 VAST 宣布完成约 30 亿元 B 轮/B+ 轮融资，发布 Tripo P2.0，首次实现原生四边面拓扑网格端到端生成。AI 3D 开启场景竞赛，迎来产业化分水岭。",
            "impact_level": "C",
            "fde_relevance": "3D/世界生成模型对推理集群提出新需求：高吞吐扩散模型服务化是 FDE 技能栈的新延伸方向。",
        },
    ],
    "Agent 应用": [
        {
            "title": "Vercel 推出 DESIGN.md：用 Markdown 解决 AI 设计 'slop' 问题",
            "source": "X @rauchg (Vercel CEO) · follow-builders feed",
            "url": "https://x.com/rauchg/status/2094541309579235680",
            "date": "2026-08-31",
            "category": "Agent 应用",
            "summary": "Vercel CEO Guillermo Rauch 宣布：下一个设计系统是 Markdown。DESIGN.md 帮助解决 AI 时代最难的问题——设计同质化（slop），并在大型组织中规模化设计品味。",
            "impact_level": "C",
            "fde_relevance": "AI 生成内容的质量治理成为新议题，Markdown 作为设计系统的思路可迁移到 Agent 输出标准化。",
        },
        {
            "title": "网易游戏建设企业级 AI Agent Infra 平台：编排/工具/记忆/安全平台化",
            "source": "网易游戏招聘",
            "url": "https://hr.game.163.com/recruit.html?cityStr=%E5%B9%BF%E5%B7%9E",
            "date": "2026-09-01",
            "category": "Agent 应用",
            "summary": "网易游戏互动娱乐事业群启动企业级 AI Agent Infra 平台建设，目标将 Agent 的运行、编排、工具、记忆、安全等通用能力平台化，降低业务构建 Agent 的成本。招聘 AI 平台研发工程师（Agent Infra 方向）。",
            "impact_level": "C",
            "fde_relevance": "Agent Infra 平台化是企业级 Agent 部署的必然趋势，对应 FDE 岗位中 Agent 基础设施方向的需求。",
        },
    ],
}


def update_jobs():
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_urls = set()
    for cat in data.get("categories", []):
        for job in cat.get("jobs", []):
            if job.get("url"):
                existing_urls.add(job["url"])

    added = 0
    for cat in data.get("categories", []):
        cat_name = cat["name"]
        if cat_name in NEW_JOBS:
            for job in NEW_JOBS[cat_name]:
                if job["url"] not in existing_urls:
                    cat["jobs"].append(job)
                    existing_urls.add(job["url"])
                    added += 1
                    print(f"  + [{cat_name}] {job['company']} - {job['title']}")

    # 重算统计
    total = sum(len(cat["jobs"]) for cat in data["categories"])
    data["total_jobs"] = total
    data["last_updated"] = "2026-09-02"

    # 重算 hot_skills
    skill_counter = Counter()
    for cat in data["categories"]:
        for job in cat["jobs"]:
            for tag in job.get("tags", []):
                skill_counter[tag] += 1
    data["hot_skills"] = [s for s, _ in skill_counter.most_common(30)]

    # 重算 hot_companies
    company_counter = Counter()
    for cat in data["categories"]:
        for job in cat["jobs"]:
            if job.get("company") and job["company"] not in ("待提取", "某大型知名互联网公司", "某大型行业公司", "某大型其他行业公司", "北京某科技公司", "长沙某中型AI+3D视觉与工业智能软件公司", "杭州某科技公司"):
                company_counter[job["company"]] += 1
    data["hot_companies"] = [c for c, _ in company_counter.most_common(25)]

    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n岗位采集完成：新增 {added} 个，总计 {total} 个")
    for cat in data["categories"]:
        print(f"  [{cat['name']}] {len(cat['jobs'])} 个")
    return added, total


def update_trends():
    with open(TRENDS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_titles = set()
    for cat in data.get("categories", []):
        for t in cat.get("trends", []):
            existing_titles.add(t["title"])

    added = 0
    for cat in data.get("categories", []):
        cat_name = cat["name"]
        if cat_name in NEW_TRENDS:
            for trend in NEW_TRENDS[cat_name]:
                if trend["title"] not in existing_titles:
                    cat["trends"].insert(0, trend)
                    existing_titles.add(trend["title"])
                    added += 1
                    print(f"  + [{cat_name}] [{trend['impact_level']}] {trend['title'][:50]}")

    total = sum(len(cat["trends"]) for cat in data["categories"])
    data["total_trends"] = total
    data["last_updated"] = "2026-09-02"

    # 更新 highlights
    s_items = []
    a_items = []
    for cat in data["categories"]:
        for t in cat["trends"]:
            if t["impact_level"] == "S" and t["date"] >= "2026-07-01":
                s_items.append(f"{t['title'][:40]}（{t['date']}）")
            elif t["impact_level"] == "A" and t["date"] >= "2026-08-01":
                a_items.append(f"{t['title'][:40]}（{t['date']}）")

    data["highlights"] = [
        {"title": "最新 S 级亮点", "items": s_items[:6]},
        {"title": "A 级趋势速览", "items": a_items[:6]},
    ]

    with open(TRENDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n趋势采集完成：新增 {added} 条，总计 {total} 条")
    for cat in data["categories"]:
        print(f"  [{cat['name']}] {len(cat['trends'])} 条")
    return added, total


if __name__ == "__main__":
    print("=" * 60)
    print("FDE 数据增量更新 — 2026-09-02")
    print("=" * 60)
    print("\n--- 岗位采集 ---")
    j_added, j_total = update_jobs()
    print("\n--- 趋势采集 ---")
    t_added, t_total = update_trends()
    print("\n" + "=" * 60)
    print(f"汇总：岗位 +{j_added}（共{j_total}），趋势 +{t_added}（共{t_total}）")
    print("=" * 60)

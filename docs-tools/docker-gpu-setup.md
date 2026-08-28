---
sidebar_position: 8
---

# Docker GPU 环境搭建

> FDE 部署工作的第一站：让容器里能直接用上 GPU。覆盖 NVIDIA Container Toolkit 安装、验证与常见坑排查。vLLM 从 0 到 1 部署实战见[动手实验](/09-labs/vllm-7b-deploy)，本篇专注环境层。

---

## 核心认知：驱动与 CUDA 的关系

容器方案最大的好处是**宿主机只装驱动，CUDA runtime 跟着镜像走**：

```
宿主机:  NVIDIA 驱动（版本够新即可，向下兼容）
        └── NVIDIA Container Toolkit（把 GPU 暴露给容器）
容器内:  CUDA Runtime / cuDNN / 框架 —— 全部由镜像自带
```

- **不需要**在宿主机装 CUDA Toolkit
- 镜像里的 CUDA 版本只要 ≤ 宿主机驱动支持的上限即可
- 查驱动支持的 CUDA 上限：`nvidia-smi` 右上角 `CUDA Version: 12.x`

---

## 安装步骤（Ubuntu 22.04 / WSL2）

### 1. 宿主机（或 WSL2）安装 NVIDIA 驱动

```bash
# Ubuntu 裸机
sudo apt install nvidia-driver-550
sudo reboot

# WSL2：不要在 WSL 内装 Linux 驱动！
# Windows 侧安装最新 Game Ready / Studio 驱动即可，WSL 自动直通
nvidia-smi   # WSL 内能输出即直通成功
```

### 2. 安装 Docker Engine + NVIDIA Container Toolkit

```bash
# Docker 官方源（略，见 Docker 文档），然后：
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 3. 验证（一条命令）

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

输出宿主机同款 `nvidia-smi` 表格即成功。

---

## 日常使用速查

```bash
# 指定 GPU（按序号或 UUID，多卡隔离必备）
docker run --gpus '"device=0,1"' ...
docker run --gpus '"device=GPU-xxxxxxxx"' ...

# docker-compose 写法
services:
  vllm:
    image: vllm/vllm-openai:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all            # 或 device_ids: ['0']
              capabilities: [gpu]
```

> `--gpus all` 是新写法；`--runtime=nvidia` 已废弃，老教程里见到直接替换。

---

## 常见坑排查

| 症状 | 原因 | 解法 |
|---|---|---|
| `could not select device driver ""` | Toolkit 未装或 docker 未重启 | 重跑 `nvidia-ctk runtime configure` + `systemctl restart docker` |
| WSL2 内 `nvidia-smi` 不存在 | 在 WSL 里装了 Linux 驱动，覆盖直通 | `sudo apt purge *nvidia*`，只用 Windows 驱动 |
| 容器内 CUDA 报版本不兼容 | 镜像 CUDA > 驱动上限 | 换低版本镜像或升级宿主机驱动 |
| 拉取 nvidia 镜像超时 | 国内网络 | 配置镜像加速器或代理后重拉 |
| 进程退出后显存未释放 | 残留进程占用 | 宿主机 `nvidia-smi` 找 PID，`docker restart` 或 kill 残留 |
| `CUDA out of memory` 但 nvidia-smi 显示空闲 | 其他容器/进程隐形占用 | `fuser -v /dev/nvidia*` 查占用者 |

---

## 相关页面

- [vLLM 7B 部署实验](/09-labs/vllm-7b-deploy) —— 环境就绪后的第一步实战
- [生产部署架构](/07-production-deployment/deployment-architecture) —— 从单容器到 K8s
- [GPU/推理服务运维工具链](/tools/gpu-ops-toolkit) —— 环境之上的监控与压测工具

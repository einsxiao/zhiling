# 知令（ZHILING）

> 全流程计算平台 · 专为科研与工程场景提效而生

知令是一款基于 **Electron + React** 的本地桌面应用。通过与 AI 智能体用自然语言协作，完成文档编写、论文修改、任务规划与执行；支持任务批量提交、实时回传、远程集群对接，让更多计算触手可及。

---

## 核心功能

| 模块 | 能力 |
|------|------|
| **AI 智能体** | 多模型对话（DeepSeek、Kimi、Doubao、Mimo 等）、流式 reasoning、tool calls、子会话 |
| **文件与项目** | 本地/远程项目、文件树、Monaco / Slate / Docx 编辑器，Markdown、PDF、表格 |
| **任务执行** | `.task` 文件、SLURM/HPC、本地/远程命令执行、任务状态轮询 |
| **数据库** | PostgreSQL、MongoDB 连接与查询 |
| **知识库** | 知识库浏览与管理 |
| **终端** | 本地 PTY 终端、SSH 远程终端 |
| **可视化** | Plotly、Mermaid、D3、ECharts 图表 |
| **邮箱** | 多账户绑定、统一收件箱、AI Agent 邮件工具 |
| **自动化** | 定时任务 + 邮件事件触发自动化 |

---

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     Electron 桌面壳                      │
├─────────────────────┬───────────────────────────────────┤
│   front_ui          │   back_frame                       │
│   React + Vite 7    │   Electron 主进程 + Node Workers   │
│   MUI 7 · Less      │   IPC · Express · ssh2 · node-pty │
└─────────────────────┴───────────────────────────────────┘
```

- **front_ui**：Vite 7 + React 19，负责 UI 与前端逻辑
- **back_frame**：Electron 主进程 + Workers，负责进程管理、IPC、系统资源与子服务

---

## 下载安装

> 最新版本：**v3.7.3**

前往 [Releases](https://github.com/einsxiao/zhiling/releases) 页面下载最新安装包。

- **Windows**：下载 `ZHILINGInstaller-*.exe` 安装程序

---

## 快速开始

### 环境要求

- **Node.js** 18+
- **yarn**（推荐）或 npm
- **Windows** 本地开发

### 安装依赖

```powershell
cd front_ui; yarn install
cd back_frame; yarn install
```

### 开发模式

1. 启动前端开发服务：

   ```powershell
   cd front_ui; yarn dev
   ```

2. 启动 Electron 应用：

   ```powershell
   cd back_frame; yarn start
   ```

### 打包发布

```powershell
cd back_frame; yarn build
```

---

## 项目结构

```
zhiling/
├── front_ui/        # 前端 React 应用（Vite、MUI、Monaco、Slate、docx 等）
├── back_frame/      # Electron 主进程与后端 Workers
├── configs/         # 各类配置文件
├── assets/          # 共享资源与配置
└── .zhiling/        # 运行时数据
```

---

## 常用命令

| 模块 | 命令 | 说明 |
|------|------|------|
| front_ui | `yarn dev` | 启动 Vite 开发服务器 |
| front_ui | `yarn build` | 构建静态资源到 dist |
| front_ui | `yarn lint` | ESLint 检查 |
| back_frame | `yarn start` | 开发模式启动 Electron |
| back_frame | `yarn build` | electron-builder 打包 |

---

## 使用说明

详细使用说明请参阅 [intro.md](./intro.md)。

---

## 许可与版权

Copyright © 2024 西安流波云信息技术有限公司

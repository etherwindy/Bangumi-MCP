# Bangumi MCP

[![License](https://img.shields.io/github/license/etherwindy/Bangumi-MCP)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io)

[English Version](README.md)

<p align="center">
  <img src="https://placehold.co/200x200/transparent/pink?font=Oswald&text=Bangumi\nM%20C%20P" alt="Bangumi MCP Logo" width="256" height="256">
</p>


<p align="center">
  一个可以访问 Bangumi API 的模型上下文协议（MCP）服务器
</p>

Bangumi MCP 是一个模型上下文协议（MCP）服务器，提供对 [Bangumi API](https://bangumi.github.io/api/) 的访问，允许用户搜索和获取有关动画、漫画和其他相关内容的信息。

## 功能

Bangumi MCP 服务器提供了一套全面的工具来与 Bangumi API 交互，包括：

### 日历和时间

- `get_current_time`：获取当前时间
- `get_calendar`：获取每周放送时间表

### 条目工具

- `search_subjects`：搜索条目，支持多种过滤器
- `get_subjects`：按类型和分类浏览条目
- `get_subject_info`：获取特定条目的详细信息
- `get_subject_persons`：获取条目的人物信息
- `get_subject_characters`：获取条目的角色信息
- `get_subject_relations`：获取相关条目

### 剧集/章节工具

- `get_episodes`：获取条目的剧集/章节信息
- `get_episode_info`：获取特定剧集/章节的详细信息

### 角色工具

- `search_characters`：搜索角色
- `get_character_info`：获取角色详细信息
- `get_character_subjects`：获取与角色相关的条目
- `get_character_persons`：获取与角色相关的人物
- `post_character_collection`：收藏角色

### 人物工具

- `search_persons`：搜索人物
- `get_person_info`：获取人物详细信息
- `get_person_subjects`：获取与人物相关的条目
- `get_person_characters`：获取与人物相关的角色
- `post_person_collection`：收藏人物

### 用户工具

- `get_user_info`：获取用户信息
- `get_me_info`：获取当前用户信息

### 收藏工具

- `get_user_collections`：获取用户的条目收藏
- `get_user_collection_info`：获取用户特定条目的收藏信息
- `post_my_collection`：为当前用户收藏条目
- `patch_my_collection`：为当前用户更新条目
- `get_my_episode_collections`：获取当前用户的剧集/章节收藏
- `patch_my_episode_collections`：更新当前用户的剧集/章节收藏
- `get_my_episode_collection_info`：获取当前用户特定剧集/章节的收藏信息
- `put_my_episode_collection_info`：更新当前用户的剧集/章节收藏
- `get_user_character_collections`：获取用户的角色收藏
- `get_user_character_collection_info`：获取用户特定角色的收藏信息
- `get_user_person_collections`：获取用户的人物收藏
- `get_user_person_collection_info`：获取用户特定人物的收藏信息

## 安装

1. 克隆仓库：

   ```bash
   git clone https://github.com/etherwindy/Bangumi-MCP.git
   cd Bangumi-MCP
   ```

2. 安装包：

   推荐使用 uv：

   ```bash
   uv pip install -e .
   ```

## 服务器配置

Bangumi MCP 服务器需要 Bangumi API 令牌才能完全发挥功能。如果使用 SSE 或者 streamable HTTP，你需要在服务启动前设置此令牌：

### 方法 1: 使用 .env 文件（推荐）

在项目根目录下创建 `.env` 文件，并添加你的 Bangumi API 令牌：

```env
BANGUMI_API_TOKEN=your_api_token_here
```

### 方法 2: 使用环境变量

直接在终端中设置环境变量：

```bash
export BANGUMI_API_TOKEN=your_api_token_here
```

在 Windows 上，使用：

```cmd
set BANGUMI_API_TOKEN=your_api_token_here
```

## 使用方法

### STDIO

直接将 json 设置导入你的 MCP 客户端应用，如 cherry-studio:

```json
{
    "mcpServers": {
        "Bangumi-MCP": {
            "command": "uv",
            "args": [
                "--directory",
                "{your_path_to_the_folder}/Bangmumi-MCP",
                "run",
                "bangumi-mcp"
            ],
            "env": {
                "BANGUMI_TOKEN": "your_token_here"
            }
        }
    }
}
```

### SSE

默认情况下，服务器将在 `localhost:18080` 上运行。可以使用 `--host` 和 `--port` 参数指定不同的主机和端口：

```bash
cd Bangumi-MCP
uv run bangumi-mcp --mode=sse --host localhost --port 18080
```

配置你的 MCP 客户端应用，例如：

```json
{
   "mcpServers": {
      "Bangumi-MCP": {
         "type": "sse",
         "url": "http://localhost:18080/sse"
      }
   }
}
```

### Streamable HTTP

默认情况下，服务器将在 `localhost:18080` 上运行。可以使用 `--host` 和 `--port` 参数指定不同的主机和端口：

```bash
cd Bangumi-MCP
uv run bangumi-mcp --mode=streamable_http --host localhost --port 18080
```

配置你的 MCP 客户端应用，例如：

```json
{
   "mcpServers": {
      "Bangumi-MCP": {
         "type": "streamableHttp",
         "url": "http://localhost:18080/mcp/"
      }
   }
}
```

## 开发

安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 鸣谢

本项目在构建过程中得到了 Qwen3-Coder 和 Claude Sonnet 4 的协助。

## 许可证

该项目采用 MIT 许可证。有关详细信息，请参见 [LICENSE](LICENSE) 文件。

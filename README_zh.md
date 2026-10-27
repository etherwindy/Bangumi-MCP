# Bangumi MCP

[![License](https://img.shields.io/github/license/etherwindy/Bangumi-MCP)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-2.x-orange)](https://modelcontextprotocol.io)

[English Version](README.md)

<p align="center">
  <img src="https://placehold.co/200x200/transparent/pink?font=Oswald&text=Bangumi\nM%20C%20P" alt="Bangumi MCP Logo" width="256" height="256">
</p>

<p align="center">
  一个可以访问 Bangumi API 的模型上下文协议（MCP）服务器
</p>

Bangumi MCP 让 MCP 客户端可以访问 [Bangumi](https://bgm.tv)（bangumi.tv）：
动画、漫画、书籍、音乐、游戏、角色、人物、目录和个人收藏。

本项目基于 **MCP Python SDK 2.3**（协议版本 **2026-07-28**），并跟随
[Bangumi OpenAPI 文档](https://bangumi.github.io/api/) 的 **2026-07-24** 版本
（内置在 `bangumi_mcp/dist.json`）。

## 主要改进

- **11 个按意图划分的工具**，而不是每个 REST 接口一个工具。工具数量大幅减少，
  但仍覆盖 Bangumi 47 个 API 路径下的全部 56 个操作。
- **自动生成并校验的 schema**：输入来自 Python 类型注解，输出来自 Pydantic 模型。
  客户端会收到 `outputSchema` 和 `structuredContent`，可以自行校验结果。
- **MCP 2.x 新特性**：工具 annotations、缓存提示（cache hints）、Resources、
  Prompts、进度通知、Streamable HTTP（有状态/无状态）以及兼容旧客户端的 SSE。
- **更贴合 Bangumi API**：正确的 `filter.tag` 搜索参数、批量章节更新、token
  scope 提示、限流重试，以及 token 过期时公开读取自动降级为匿名请求。

## 快速开始

```bash
git clone https://github.com/etherwindy/Bangumi-MCP.git
cd Bangumi-MCP
uv sync
uv run bangumi-mcp --help
```

配置 Bangumi 访问令牌（公开读取可以不配，`/v0/me` 和所有写操作必须配置）：

```env
# .env
BANGUMI_API_TOKEN=your_api_token_here
```

令牌在 <https://next.bgm.tv/demo/access-token> 生成。当前 Bangumi 规范为写接口
标注了 OAuth scope：

| Scope              | 用途                                              |
| ------------------ | ------------------------------------------------- |
| `write:collection` | 条目/章节收藏，收藏角色、人物、目录               |
| `write:indices`    | 创建/编辑目录及其条目                             |

返回 403 时会附带提示，说明缺少哪个 scope。

## 工具

所有工具都带有 `readOnlyHint`、`destructiveHint`、`idempotentHint` 和
`openWorldHint` 注解。

| 工具 | 功能 | 对应接口 |
| ---- | ---- | -------- |
| `bangumi_search` | 按关键词搜索条目、角色或人物。条目搜索支持类型、标签、元标签、放送日期、评分、评分人数、排名和 NSFW 过滤。 | `POST /v0/search/{subjects,characters,persons}` |
| `bangumi_browse_subjects` | 按类型/分类/年份/月份/平台/系列浏览条目，可按日期或排名排序。 | `GET /v0/subjects` |
| `bangumi_get_subject` | 条目详情（简介、infobox、评分、标签、图片、收藏统计）。`include` 可一次附带角色、人物、相关条目和/或章节。 | `GET /v0/subjects/{id}` 及相关接口 |
| `bangumi_get_episodes` | 列出条目章节，或获取单个章节。 | `GET /v0/episodes`, `GET /v0/episodes/{id}` |
| `bangumi_get_entity` | 角色或人物详情；`include` 可附带其参与作品以及关联角色/人物。 | `GET /v0/{characters,persons}/{id}` 及相关接口 |
| `bangumi_get_revisions` | 获取条目/章节/角色/人物的修订历史，或单条修订详情。 | `GET /v0/revisions/*` |
| `bangumi_get_user` | 按用户名获取用户资料；省略 `username` 时获取当前登录用户。 | `GET /v0/users/{username}`, `GET /v0/me` |
| `bangumi_get_collections` | 读取任意用户的条目/角色/人物收藏，以及当前用户的章节进度。 | `GET /v0/users/*/collections*` |
| `bangumi_update_collection` | 写入收藏状态：条目状态/评分/评论/标签/进度，单集或批量章节状态，收藏/取消收藏角色、人物、目录。 | `POST/PATCH /v0/users/-/collections*`, `POST/DELETE /v0/*/collect` |
| `bangumi_manage_index` | 创建/读取/更新目录，列出/添加/修改/删除目录条目，收藏/取消收藏目录。 | `/v0/indices*` |
| `bangumi_get_calendar` | 每周放送时间表。 | `GET /calendar` |

> 已知上游限制：Bangumi API 文档中声明了
> `DELETE /v0/characters/{id}/collect` 和 `DELETE /v0/persons/{id}/collect`，
> 但服务端尚未实现
> （[bangumi/api#234](https://github.com/bangumi/api/issues/234)）。
> 因此对角色/人物执行 `bangumi_update_collection(action="unset")` 会返回明确
> 错误；目前请到 <https://bgm.tv> 网页端取消收藏。

图片 URL 已经包含在条目/角色/人物/用户数据里，因此不再单独提供图片工具。
`bangumi_get_subject(subject_id=..., include=[...])` 取代了旧的
`get_subject_info` / `get_subject_persons` / `get_subject_characters` /
`get_subject_relations` 系列工具。

### 从 0.1.x 迁移

旧的 55 个接口型工具已合并为上面的 11 个工具，功能没有缺失。

| 旧工具 | 新工具 |
| ------ | ------ |
| `search_subjects`, `search_characters`, `search_persons` | `bangumi_search` |
| `get_subjects` | `bangumi_browse_subjects` |
| `get_subject_info`, `get_subject_image`, `get_subject_persons`, `get_subject_characters`, `get_subject_relations` | `bangumi_get_subject`（`include=[...]`，图片在返回数据中） |
| `get_episodes`, `get_episode_info` | `bangumi_get_episodes`（`subject_id` 或 `episode_id`） |
| `get_character_info`, `get_character_image`, `get_character_subjects`, `get_character_persons` | `bangumi_get_entity`（`entity=character`, `include=[...]`） |
| `get_person_info`, `get_person_image`, `get_person_subjects`, `get_person_characters` | `bangumi_get_entity`（`entity=person`, `include=[...]`） |
| 8 个 `get_*_revision*` 工具 | `bangumi_get_revisions` |
| `get_user_info`, `get_user_avatar`, `get_me_info` | `bangumi_get_user` |
| `get_user_collections`, `get_user_collection_info`, `get_my_episode_collections`, `get_my_episode_collection_info`, `get_user_character_collections*`, `get_user_person_collections*` | `bangumi_get_collections` |
| `post_my_collection`, `patch_my_collection`, `patch_my_episode_collections`, `put_my_episode_collection_info`, `post/delete_character_collection`, `post/delete_person_collection`, `post/delete_index_collection` | `bangumi_update_collection` |
| 全部 9 个目录工具 | `bangumi_manage_index`（`action=...`） |
| `get_calendar` | `bangumi_get_calendar` |
| `get_current_time` | 已移除（宿主本身知道当前时间） |

## 使用的 MCP 特性

- **SDK 2.x / `MCPServer`**：高层服务器类（原 `FastMCP`）。处理函数是带类型的
  普通函数，schema 由类型注解生成，不再手写维护。
- **协议 2026-07-28**：现代连接不再有握手和会话；支持 `tools/list` 与
  `resources/read` 缓存提示以及按请求路由的 header。同一进程仍兼容 2025 版
  协议客户端（包括旧版 HTTP+SSE）。
- **结构化输出**：每个工具都声明 `outputSchema`，结果同时返回文本和
  `structuredContent`。客户端会校验结构化内容，因此 Bangumi 中可空的字段都被
  建模为 nullable，并在输出时去掉 `null`。
- **Annotations 与标题**：每个工具都有可读标题和 MCP 提示
  （`readOnlyHint`、`destructiveHint`、`idempotentHint`、`openWorldHint`）。
- **Resources**：`bangumi://calendar`，以及
  `bangumi://subject/{id}`、`bangumi://character/{id}`、
  `bangumi://person/{id}`、`bangumi://user/{username}` 模板，客户端可以不调用
  工具直接读取条目数据。
- **Prompts**：`bangumi_recommend`、`bangumi_subject_deep_dive`、
  `bangumi_backlog_review` 提供现成的工作流模板。
- **进度通知**：`bangumi_get_subject`、`bangumi_get_entity` 在并发加载关联
  数据时会报告进度。
- **传输控制**：`--stateless` 使用无会话的 Streamable HTTP，
  `--json-response` 返回普通 JSON 而不是 SSE 流。

## 配置

| 环境变量 | 默认值 | 说明 |
| -------- | ------ | ---- |
| `BANGUMI_API_TOKEN` | 未设置 | Bangumi 访问令牌。公开读取无需令牌。 |
| `BANGUMI_API_BASE_URL` | `https://api.bgm.tv` | 覆盖 API 根地址（代理/测试）。 |

工作目录下的 `.env` 会自动加载。如果配置了但已过期的 token，公开读取会自动
匿名重试；只有需要认证的调用会失败，并给出令牌页面提示。

## 使用方法

### STDIO

```json
{
  "mcpServers": {
    "Bangumi-MCP": {
      "command": "uv",
      "args": ["--directory", "/path/to/Bangumi-MCP", "run", "bangumi-mcp"],
      "env": {
        "BANGUMI_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Streamable HTTP

```bash
uv run bangumi-mcp --mode=streamable_http --host localhost --port 18080
```

```json
{
  "mcpServers": {
    "Bangumi-MCP": {
      "type": "streamableHttp",
      "url": "http://localhost:18080/mcp"
    }
  }
}
```

添加 `--stateless` 可完全禁用服务端会话，添加 `--json-response` 可接收普通
JSON 响应。

### SSE（旧客户端）

```bash
uv run bangumi-mcp --mode=sse --host localhost --port 18080
```

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

SSE 仅用于仍使用 2025 版握手的旧客户端，新客户端建议使用 Streamable HTTP。

## 开发

```bash
uv sync
uv run pytest
uv run python scripts/update_openapi.py --check   # 检查内置 schema 是否过期
uv run python scripts/update_openapi.py           # 更新 schema
```

目录结构：

```text
bangumi_mcp/
  __main__.py        CLI（stdio / sse / streamable_http）
  mcp_server.py      MCPServer 工厂、传输层、缓存提示
  bangumi_client.py  httpx 客户端、重试、错误映射
  models.py          用于输出 schema 的 Pydantic 模型
  resources.py       MCP Resources
  prompts.py         MCP Prompts
  tools/             按工具组拆分的模块
scripts/update_openapi.py
tests/
```

更新 OpenAPI 文档后，请检查 diff，并在接口或数据结构变化时同步修改
`bangumi_mcp/models.py`、`bangumi_mcp/bangumi_client.py` 和工具描述。

## 鸣谢

项目最初在 Qwen3-Coder 和 Claude Sonnet 4 的协助下完成。

## 许可证

MIT，详见 [LICENSE](LICENSE)。

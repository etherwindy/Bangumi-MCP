# Bangumi MCP

[![License](https://img.shields.io/github/license/etherwindy/Bangumi-MCP)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io)

[中文版本](README_zh.md)

<p align="center">
  <img src="https://placehold.co/200x200/transparent/pink?font=Oswald&text=Bangumi\nM%20C%20P" alt="Bangumi MCP Logo" width="256" height="256">
</p>

<p align="center">
  A Model Context Protocol (MCP) server for accessing Bangumi API
</p>

Bangumi MCP is a Model Context Protocol (MCP) server that provides access to the [Bangumi API](https://bangumi.github.io/api/), allowing users to search for and retrieve information about anime, manga, and other related content.

## Features

The Bangumi MCP server provides a comprehensive set of tools for interacting with the Bangumi API, including:

The project tracks the Bangumi OpenAPI schema bundled in `bangumi_mcp/dist.json` and currently targets the `2026-05-2` API schema. It requires `mcp>=1.27.2` and uses modern MCP features such as tool output schemas, structured tool results, tool annotations, and Streamable HTTP.

### Calendar and Time

- `get_current_time`: Get the current time
- `get_calendar`: Get the weekly broadcast schedule

### Subject Tools

- `search_subjects`: Search for subjects with various filters
- `get_subjects`: Browse subjects by type and category
- `get_subject_info`: Get detailed information about a specific subject
- `get_subject_image`: Get a subject image URL
- `get_subject_persons`: Get person information for a subject
- `get_subject_characters`: Get character information for a subject
- `get_subject_relations`: Get related subjects

### Episode Tools

- `get_episodes`: Get episode information for a subject
- `get_episode_info`: Get detailed information about a specific episode

### Revision Tools

- `get_subject_revisions`: Get subject revision history
- `get_subject_revision_info`: Get subject revision details
- `get_episode_revisions`: Get episode revision history
- `get_episode_revision_info`: Get episode revision details
- `get_character_revisions`: Get character revision history
- `get_character_revision_info`: Get character revision details
- `get_person_revisions`: Get person revision history
- `get_person_revision_info`: Get person revision details

### Character Tools

- `search_characters`: Search for characters
- `get_character_info`: Get detailed character information
- `get_character_image`: Get a character image URL
- `get_character_subjects`: Get subjects related to a character
- `get_character_persons`: Get persons related to a character
- `post_character_collection`: Collect a character

### Person Tools

- `search_persons`: Search for persons
- `get_person_info`: Get detailed person information
- `get_person_image`: Get a person image URL
- `get_person_subjects`: Get subjects related to a person
- `get_person_characters`: Get characters related to a person
- `post_person_collection`: Collect a person

### Index Tools

- `post_index`: Create an index for the current user
- `get_index_info`: Get index information
- `put_index`: Update index information
- `post_index_collection`: Collect an index
- `delete_index_collection`: Uncollect an index
- `get_index_subjects`: Get subjects in an index
- `post_index_subject`: Add a subject to an index
- `put_index_subject`: Update a subject in an index
- `delete_index_subject`: Delete a subject from an index

### User Tools

- `get_user_info`: Get user information
- `get_user_avatar`: Get a user avatar URL
- `get_me_info`: Get current user information

### Collection Tools

- `get_user_collections`: Get user's subject collections
- `get_user_collection_info`: Get user's collection info for a specific subject
- `post_my_collection`: Collect a subject for the current user
- `patch_my_collection`: Update a subject collection for the current user
- `get_my_episode_collections`: Get current user's episode collections
- `patch_my_episode_collections`: Update current user's episode collection
- `get_my_episode_collection_info`: Get current user's episode collection info for a specific episode
- `put_my_episode_collection_info`: Update current user's episode collection
- `get_user_character_collections`: Get user's character collections
- `get_user_character_collection_info`: Get user's character collection info for a specific character
- `get_user_person_collections`: Get user's person collections
- `get_user_person_collection_info`: Get user's person collection info for a specific person

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/etherwindy/Bangumi-MCP.git
   cd Bangumi-MCP
   ```

2. Install dependencies:

   It is recommended to use uv. The project includes a standard build configuration, so the `bangumi-mcp` console script is available after syncing:

   ```bash
   uv sync
   uv run bangumi-mcp --help
   ```

   You can also install it into another environment with `uv pip install -e .`.

## Server Configuration

The Bangumi MCP server requires a Bangumi API token for full functionality. If you use SSE or streamable HTTP, you need to configure this token before the server starts:

### Method 1: Using a .env file (Recommended)

Create a `.env` file in the project root directory with your Bangumi API token:

```env
BANGUMI_API_TOKEN=your_api_token_here
```

### Method 2: Using Environment Variables

Set the environment variable directly in your terminal:

```bash
export BANGUMI_API_TOKEN=your_api_token_here
```

On Windows, use:

```cmd
set BANGUMI_API_TOKEN=your_api_token_here
```

## Usage

### STDIO

Import this JSON config into your MCP client application, such as Cherry Studio:

```json
{
    "mcpServers": {
        "Bangumi-MCP": {
            "command": "uv",
            "args": [
                "--directory",
                "{your_path_to_the_folder}/Bangumi-MCP",
                "run",
                "bangumi-mcp"
            ],
            "env": {
                "BANGUMI_API_TOKEN": "your_token_here"
            }
        }
    }
}
```

### SSE

By default, the server will run on `localhost:18080`. You can specify a different host and port using the `--host` and `--port` arguments:

```bash
cd Bangumi-MCP
uv run bangumi-mcp --mode=sse --host localhost --port 18080
```

Configure your MCP client application, for example:

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

By default, the server will run on `localhost:18080`. You can specify a different host and port using the `--host` and `--port` arguments:

```bash
cd Bangumi-MCP
uv run bangumi-mcp --mode=streamable_http --host localhost --port 18080
```

Configure your MCP client application, for example:

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

## Modern MCP Support

- Tool responses include `structuredContent` when the underlying tool returns structured JSON data, while still including readable JSON text for compatibility.
- Tool metadata includes MCP annotations such as `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint`.
- The server supports STDIO, SSE, and Streamable HTTP transports.
- Mutating tools require a valid `BANGUMI_API_TOKEN`; read-only public API tools can be used without a token where Bangumi allows it.

## Acknowledgements

This project was built with the assistance of Qwen3-Coder and Claude Sonnet 4.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

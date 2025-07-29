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

Bangumi MCP is a Model Context Protocol (MCP) server that provides access to the [Banguimi API](https://bangumi.github.io/api/), allowing users to search for and retrieve information about anime, manga, and other related content.

## Features

The Bangumi MCP server provides a comprehensive set of tools for interacting with the Bangumi API, including:

### Calendar and Time

- `get_current_time`: Get the current time
- `get_calendar`: Get the weekly broadcast schedule

### Subject Tools

- `search_subjects`: Search for subjects with various filters
- `get_subjects`: Browse subjects by type and category
- `get_subject_info`: Get detailed information about a specific subject
- `get_subject_persons`: Get person information for a subject
- `get_subject_characters`: Get character information for a subject
- `get_subject_relations`: Get related subjects

### Episode Tools

- `get_episodes`: Get episode information for a subject
- `get_episode_info`: Get detailed information about a specific episode

### Character Tools

- `search_characters`: Search for characters
- `get_character_info`: Get detailed character information
- `get_character_subjects`: Get subjects related to a character
- `get_character_persons`: Get persons related to a character
- `post_character_collection`: Collect a character

### Person Tools

- `search_persons`: Search for persons
- `get_person_info`: Get detailed person information
- `get_person_subjects`: Get subjects related to a person
- `get_person_characters`: Get characters related to a person
- `post_person_collection`: Collect a person

### User Tools

- `get_user_info`: Get user information
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

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Server Configuration

The Bangumi MCP server requires a Bangumi API token for full functionality. There are two ways to configure this token:

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

To start the MCP server:

```bash
python main.py
```

By default, the server will run on `localhost:18080`. You can specify a different host and port using the `--host` and `--port` arguments:

```bash
python main.py --host 0.0.0.0 --port 8080
```

Config your MCP client application, for example:

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

## Development

To install development dependencies:

```bash
pip install -e ".[dev]"
```

## Acknowledgements

This project was built with the assistance of Qwen3-Coder and Claude Sonnet 4.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

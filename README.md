# Metabase MCP Server

This is a Python implementation of a Model Context Protocol (MCP) server that integrates with Metabase API, allowing Large Language Models (LLMs) to interact with Metabase data and functionality.

## Features

- View dashboards and their contents
- List and execute questions/cards
- Access database information
- Execute SQL queries against Metabase databases
- Full support for MCP resources and tools

## Prerequisites

- Python 3.9 or higher
- A running Metabase instance
- Metabase user credentials with appropriate permissions

## Installation

1. Install the MCP SDK:

```bash
pip install "mcp[cli]"
```

2. Set environment variables for Metabase connection:

```bash
# Windows
set METABASE_URL=https://your-metabase-instance.com
set METABASE_USERNAME=your_username
set METABASE_PASSWORD=your_password

# Linux/macOS
export METABASE_URL=https://your-metabase-instance.com
export METABASE_USERNAME=your_username
export METABASE_PASSWORD=your_password
```

## Usage

### Running the Server

```bash
python metabase_mcp_server.py
```

### Installing in Claude Desktop

You can install this server in Claude Desktop for direct interaction:

```bash
mcp install metabase_mcp_server.py
```

### Testing with MCP Inspector

Test your server with the MCP Inspector:

```bash
mcp dev metabase_mcp_server.py
```

## Available Resources

- `metabase://dashboard/{dashboard_id}` - Get a specific dashboard
- `metabase://card/{card_id}` - Get a specific question/card
- `metabase://database/{database_id}` - Get a specific database

## Available Tools

- `list_dashboards` - List all dashboards
- `list_cards` - List all questions/cards
- `list_databases` - List all databases
- `execute_card` - Execute a specific card/question
- `get_dashboard_cards` - Get cards in a dashboard
- `execute_query` - Run SQL against a Metabase database

## Example Usage in LLM Prompts

```
To interact with Metabase:
1. Use list_dashboards to see available dashboards
2. Use get_dashboard_cards to view cards in a dashboard
3. Use execute_card to run a specific question
4. Use execute_query to run custom SQL

For example, to get sales data:
- Find the sales dashboard ID
- Get cards in that dashboard
- Execute the relevant sales card
```

## Error Handling

The server includes comprehensive error handling and logging to help diagnose issues with Metabase API connections.

## Development

Feel free to extend this MCP server with additional functionality by adding more resources and tools as needed.

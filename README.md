# notion-multi-mcp

[English](#english) | [繁體中文](#繁體中文)

---

## English

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that lets AI assistants operate **multiple Notion accounts** simultaneously. Each account gets its own prefixed toolset — no conflicts, no mix-ups.

### Features

- **Multi-account** — connect 2, 3, or more Notion workspaces in a single MCP server
- **Custom prefixes** — you name each account (e.g. `work`, `personal`, `team`), tools are auto-generated as `work_search`, `personal_create_page`, `team_query_database`, etc.
- **22 tools per account** — full Notion API coverage: pages, databases, blocks, comments, data sources, search
- **Zero conflict** — each account is fully isolated with its own API key and client instance

### Quick Start

#### Install

```bash
pip install notion-multi-mcp
```

Or run directly without installing:

```bash
uvx notion-multi-mcp
```

#### Configure in Claude Code

```bash
claude mcp add notion-multi -- uvx notion-multi-mcp
```

Then set the environment variable in your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "notion-multi": {
      "command": "uvx",
      "args": ["notion-multi-mcp"],
      "env": {
        "NOTION_ACCOUNTS": "work:ntn_your_work_key,personal:ntn_your_personal_key"
      }
    }
  }
}
```

#### Configure in Cursor / VS Code

Add to `.cursor/mcp.json` or `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "notion-multi": {
      "command": "uvx",
      "args": ["notion-multi-mcp"],
      "env": {
        "NOTION_ACCOUNTS": "work:ntn_your_work_key,personal:ntn_your_personal_key"
      }
    }
  }
}
```

### Configuration

Set `NOTION_ACCOUNTS` with comma-separated `prefix:api_key` pairs:

```
NOTION_ACCOUNTS=work:ntn_abc123,personal:ntn_def456,team:ntn_ghi789
```

This example creates **3 accounts × 22 tools = 66 tools**:

- `work_search`, `work_create_page`, `work_query_database`, ...
- `personal_search`, `personal_create_page`, `personal_query_database`, ...
- `team_search`, `team_create_page`, `team_query_database`, ...

### Getting Notion API Keys

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **"New integration"** for each workspace
3. Copy the **Internal Integration Secret** (starts with `ntn_`)
4. **Important**: In Notion, share the pages/databases you want to access with your integration

### Available Tools (per account)

Each connected account gets all 22 tools, prefixed with the account name:

| # | Tool | Description |
|---|------|-------------|
| 1 | `{prefix}_search` | Search pages and databases |
| 2 | `{prefix}_query_database` | Query database contents with filters and sorts |
| 3 | `{prefix}_create_page` | Create a new page |
| 4 | `{prefix}_retrieve_page` | Get page information |
| 5 | `{prefix}_update_page` | Update page properties |
| 6 | `{prefix}_retrieve_page_property` | Get a specific page property |
| 7 | `{prefix}_move_page` | Move a page to a new parent |
| 8 | `{prefix}_retrieve_block` | Get block information |
| 9 | `{prefix}_update_block` | Update a block |
| 10 | `{prefix}_delete_block` | Delete a block |
| 11 | `{prefix}_get_block_children` | List child blocks |
| 12 | `{prefix}_append_block_children` | Append child blocks |
| 13 | `{prefix}_retrieve_database` | Get database schema |
| 14 | `{prefix}_create_database` | Create a new database |
| 15 | `{prefix}_update_database` | Update database properties |
| 16 | `{prefix}_query_data_source` | Query a data source |
| 17 | `{prefix}_retrieve_data_source` | Get data source info |
| 18 | `{prefix}_list_data_source_templates` | List data source templates |
| 19 | `{prefix}_update_data_source` | Update a data source |
| 20 | `{prefix}_create_comment` | Create a comment |
| 21 | `{prefix}_retrieve_comments` | List comments |
| 22 | `{prefix}_get_self` | Get bot user info |

### Usage Examples

Once configured, you can ask your AI assistant:

- *"Search for 'Q1 Report' in my work Notion"* → `work_search`
- *"Create a new page in my personal Notion"* → `personal_create_page`
- *"Copy the database schema from work to team"* → `work_retrieve_database` + `team_create_database`
- *"List all pages in both accounts"* → `work_search` + `personal_search` in parallel

### Requirements

- Python 3.10+
- Notion integration API keys ([create here](https://www.notion.so/my-integrations))

### Development

```bash
git clone https://github.com/kerwin77106/Notion-Multi-MCP.git
cd notion-multi-mcp

pip install -r requirements.txt

export NOTION_ACCOUNTS="dev:ntn_your_key_here"

python notion_multi_mcp.py
```

### License

[MIT](LICENSE)

---

## 繁體中文

一個 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 伺服器，讓 AI 助手能**同時操作多個 Notion 帳號**。每個帳號擁有獨立的前綴工具集，不會混淆、不會衝突。

### 功能特色

- **多帳號支援** — 可連接 2 個、3 個甚至更多 Notion 工作區
- **自訂前綴** — 自由命名帳號（如 `work`、`personal`、`team`），工具會自動產生為 `work_search`、`personal_create_page`、`team_query_database` 等
- **每帳號 22 個工具** — 完整覆蓋 Notion API：頁面、資料庫、區塊、評論、資料來源、搜尋
- **完全隔離** — 每個帳號使用獨立的 API Key 和 Client 實例

### 快速開始

#### 安裝

```bash
pip install notion-multi-mcp
```

或直接執行（不需安裝）：

```bash
uvx notion-multi-mcp
```

#### 在 Claude Code 中設定

```bash
claude mcp add notion-multi -- uvx notion-multi-mcp
```

然後在 Claude Code 設定檔（`~/.claude/settings.json`）中設定環境變數：

```json
{
  "mcpServers": {
    "notion-multi": {
      "command": "uvx",
      "args": ["notion-multi-mcp"],
      "env": {
        "NOTION_ACCOUNTS": "work:ntn_你的工作帳號金鑰,personal:ntn_你的個人帳號金鑰"
      }
    }
  }
}
```

#### 在 Cursor / VS Code 中設定

新增到 `.cursor/mcp.json` 或 `.vscode/mcp.json`：

```json
{
  "mcpServers": {
    "notion-multi": {
      "command": "uvx",
      "args": ["notion-multi-mcp"],
      "env": {
        "NOTION_ACCOUNTS": "work:ntn_你的工作帳號金鑰,personal:ntn_你的個人帳號金鑰"
      }
    }
  }
}
```

### 設定方式

設定 `NOTION_ACCOUNTS` 環境變數，用逗號分隔 `前綴:API金鑰` 組合：

```
NOTION_ACCOUNTS=work:ntn_abc123,personal:ntn_def456,team:ntn_ghi789
```

以上範例會產生 **3 個帳號 × 22 個工具 = 66 個工具**：

- `work_search`、`work_create_page`、`work_query_database`⋯
- `personal_search`、`personal_create_page`、`personal_query_database`⋯
- `team_search`、`team_create_page`、`team_query_database`⋯

### 取得 Notion API Key

1. 前往 [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. 為每個要連接的工作區點擊 **「New integration」**
3. 複製 **Internal Integration Secret**（以 `ntn_` 開頭）
4. **重要**：在 Notion 中，將你要存取的頁面/資料庫分享給你建立的 Integration

### 可用工具（每個帳號各一套）

每個連接的帳號都會取得全部 22 個工具，工具名稱加上帳號前綴：

| # | 工具名稱 | 說明 |
|---|---------|------|
| 1 | `{前綴}_search` | 搜尋頁面和資料庫 |
| 2 | `{前綴}_query_database` | 查詢資料庫內容（支援篩選和排序） |
| 3 | `{前綴}_create_page` | 建立新頁面 |
| 4 | `{前綴}_retrieve_page` | 取得頁面資訊 |
| 5 | `{前綴}_update_page` | 更新頁面屬性 |
| 6 | `{前綴}_retrieve_page_property` | 取得特定頁面屬性 |
| 7 | `{前綴}_move_page` | 將頁面移動到新的父頁面 |
| 8 | `{前綴}_retrieve_block` | 取得區塊資訊 |
| 9 | `{前綴}_update_block` | 更新區塊 |
| 10 | `{前綴}_delete_block` | 刪除區塊 |
| 11 | `{前綴}_get_block_children` | 列出子區塊 |
| 12 | `{前綴}_append_block_children` | 追加子區塊 |
| 13 | `{前綴}_retrieve_database` | 取得資料庫結構 |
| 14 | `{前綴}_create_database` | 建立新資料庫 |
| 15 | `{前綴}_update_database` | 更新資料庫屬性 |
| 16 | `{前綴}_query_data_source` | 查詢資料來源 |
| 17 | `{前綴}_retrieve_data_source` | 取得資料來源資訊 |
| 18 | `{前綴}_list_data_source_templates` | 列出資料來源範本 |
| 19 | `{前綴}_update_data_source` | 更新資料來源 |
| 20 | `{前綴}_create_comment` | 建立評論 |
| 21 | `{前綴}_retrieve_comments` | 列出評論 |
| 22 | `{前綴}_get_self` | 取得 Bot 使用者資訊 |

### 使用範例

設定完成後，你可以對 AI 助手說：

- 「在我的 work Notion 搜尋『Q1 報告』」→ 呼叫 `work_search`
- 「在 personal Notion 建一個新頁面」→ 呼叫 `personal_create_page`
- 「把 work 的資料庫結構複製到 team」→ 呼叫 `work_retrieve_database` + `team_create_database`
- 「列出兩個帳號的所有頁面」→ 同時呼叫 `work_search` 和 `personal_search`

### 系統需求

- Python 3.10+
- Notion Integration API Key（[在此建立](https://www.notion.so/my-integrations)）

### 開發

```bash
git clone https://github.com/kerwin77106/Notion-Multi-MCP.git
cd notion-multi-mcp

pip install -r requirements.txt

export NOTION_ACCOUNTS="dev:ntn_你的金鑰"

python notion_multi_mcp.py
```

### 授權

[MIT](LICENSE)

# 🤖 AI SQL Assistant

A complete, enterprise-grade, beginner-friendly **AI SQL Assistant** built with **Python, FastAPI, PostgreSQL, SQLAlchemy, AST SQL Security Validation, and LLM Integration (Gemini / OpenAI / Mock)**.

Convert plain English questions directly into safe, validated PostgreSQL read-only queries with interactive tabular results and step-by-step explanations!

---

## 🏗️ Required Architecture

```text
               User Question
                     │
                     ▼
             ┌───────────────┐
             │    FastAPI    │
             └───────┬───────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Question Processor   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ DB Schema Retriever   │ (Dynamic SQLAlchemy Inspector)
         └───────────┬───────────┘
                     │
                     ▼
             ┌───────────────┐
             │    LLM API    │ (Gemini / OpenAI / Mock)
             └───────┬───────┘
                     │ (JSON Output: SQL + Explanation)
                     ▼
         ┌───────────────────────┐
         │  AST SQL Validator    │ (Strict SELECT-only + Blacklist)
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ Read-Only PostgreSQL  │ (Timeout & Limit Enforced)
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Result Formatter    │
         └───────────┬───────────┘
                     │
                     ▼
                User Result
```

---

## ✨ Features

- 🧠 **Natural Language to SQL**: Converts questions like *"Show me users who registered this month"* into clean PostgreSQL queries.
- 🔒 **Defense-in-Depth Security**:
  - AST Parsing & Validation via `sqlglot`.
  - Read-Only `SELECT` enforcement.
  - Keyword Blacklist (blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, etc.).
  - Multi-statement injection prevention (rejects `;` multiplexing).
  - Schema Table Whitelist Enforcement (prevents accessing unauthorized or non-existent tables).
  - Automatic `LIMIT` cap injection (default `LIMIT 100`).
  - Query timeout guardrail.
  - Dedicated PostgreSQL **read-only database user**.
- 📊 **Dynamic Database Schema Retriever**: Automatically inspects table names, columns, data types, primary keys, and foreign keys via SQLAlchemy `inspect` instead of hardcoding schema prompts.
- 💡 **Plain English Explanation**: Returns concise explanations for every generated query.
- 🎨 **Glassmorphism Web Dashboard**: Modern responsive UI with 10 sample prompt chips, visual schema modal inspector, copy-to-clipboard, and live query execution latency stats.
- 🔄 **Multi-Provider LLM Integration**: Natively supports Google Gemini (`google-genai`), OpenAI API, and an offline **Mock Provider** for immediate zero-key execution.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic V2
- **Database**: PostgreSQL / SQLite (zero-config local engine)
- **AI / LLM**: Google Gemini API, OpenAI API, Structured JSON Output
- **Security & AST**: `sqlglot`, `sqlparse`
- **Frontend**: HTML5, CSS3 Glassmorphism, Vanilla JS
- **DevOps**: Docker, Docker Compose, Pytest

---

## 📁 Project Structure

```text
ai-sql-assistant/
│
├── app/
│   ├── main.py                     # FastAPI app initialization & route mounting
│   ├── config.py                   # Pydantic settings loading from .env
│   ├── database.py                 # SQLAlchemy engine & session setup
│   ├── models/
│   │   ├── schema.py               # User, Product, Order, Payment ORM models
│   │   └── dto.py                  # Pydantic request/response schemas
│   ├── routes/
│   │   ├── health.py               # GET /health
│   │   ├── schema.py               # GET /schema
│   │   ├── query.py                # POST /query
│   │   └── explain.py              # POST /explain
│   ├── services/
│   │   ├── schema_service.py       # Dynamic schema & DDL generator
│   │   ├── llm_service.py          # Gemini / OpenAI / Mock LLM provider
│   │   ├── sql_generator.py        # System prompt builder & JSON parser
│   │   └── sql_validator.py        # AST SQL parsing & safety guardrails
│   ├── static/                     # Web UI frontend (HTML/CSS/JS)
│   └── utils/
│       └── formatter.py            # Query execution & result formatter
│
├── tests/
│   ├── test_validator.py           # SQL safety & injection test suite
│   └── test_api.py                 # Endpoint integration tests
│
├── scripts/
│   ├── seed_db.py                  # Python database seeder with realistic data
│   └── init_db.sql                 # PostgreSQL DDL & read-only user setup
│
├── docker-compose.yml              # PostgreSQL + App Docker setup
├── Dockerfile                      # Application container specification
├── requirements.txt                # Dependencies list
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore file
└── README.md                       # Documentation
```

---

## 🚀 Step-by-Step Setup Guide

### Option 1: Quick Local Run (Zero External Dependencies)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ai-sql-assistant.git
   cd ai-sql-assistant
   ```

2. **Create Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *(By default, `LLM_PROVIDER=mock` and `DB_ENGINE=sqlite` are active, enabling immediate execution without requiring an API key or running PostgreSQL!)*

4. **Seed Sample Database**:
   ```bash
   python scripts/seed_db.py
   ```

5. **Start FastAPI Application Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Open your browser at: **[http://localhost:8000](http://localhost:8000)**

---

### Option 2: Production Setup with PostgreSQL & Docker Compose

1. **Start Containers**:
   ```bash
   docker-compose up --build -d
   ```

2. **Check Logs & Status**:
   ```bash
   docker-compose logs -f app
   ```

3. **Access Application**:
   - Web Dashboard: **[http://localhost:8000](http://localhost:8000)**
   - OpenAPI Swagger Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 📡 API Documentation & Sample Requests

### 1. `GET /health`
Returns system health, database status, and LLM configuration.

**Response**:
```json
{
  "status": "ok",
  "app_name": "AI SQL Assistant",
  "database": {
    "engine": "sqlite",
    "status": "healthy"
  },
  "llm_provider": "mock",
  "model": "gemini-2.5-flash"
}
```

---

### 2. `GET /schema`
Dynamically retrieves current database schema tables, column types, primary keys, and foreign keys.

---

### 3. `POST /query`
Converts natural language into validated SQL and executes it against the database.

**Request**:
```json
POST /query
Content-Type: application/json

{
  "question": "Show me users who registered this month"
}
```

**Response**:
```json
{
  "question": "Show me users who registered this month",
  "sql": "SELECT id, name, email, role, created_at FROM users WHERE created_at >= '2026-09-01' ORDER BY created_at DESC LIMIT 100",
  "explanation": "This query selects all users who registered during the current month (September 2026), ordered by registration date.",
  "columns": ["id", "name", "email", "role", "created_at"],
  "rows": [
    [1, "Arun Kumar", "arun@example.com", "customer", "2026-09-15T19:17:00+00:00"],
    [2, "Bala Ram", "bala@example.com", "customer", "2026-09-18T19:17:00+00:00"],
    [6, "Vikram Singh", "vikram@example.com", "customer", "2026-09-19T19:17:00+00:00"]
  ],
  "row_count": 3,
  "execution_time_ms": 1.45,
  "tables_used": ["users"],
  "confidence": 0.98
}
```

---

### 4. `POST /explain`
Validates standalone SQL and generates plain English explanation without executing.

---

## 🎯 10 Realistic Demo Questions

| # | Demo Question | SQL Capabilities Demonstrated |
|---|---|---|
| 1 | *"Show me users who registered this month"* | Date Filtering & Sorting (`WHERE created_at >= ...`) |
| 2 | *"What are the top 5 most expensive products?"* | Sorting & Ordering (`ORDER BY price DESC LIMIT 5`) |
| 3 | *"Count total completed orders grouped by payment method"* | Table Join & Group Aggregation (`JOIN`, `GROUP BY`, `SUM`, `COUNT`) |
| 4 | *"Find total revenue generated from completed orders"* | Aggregation Function (`SUM(total_amount)`) |
| 5 | *"List users who have placed more than 2 orders"* | Having Aggregation Filter (`GROUP BY`, `HAVING COUNT >= 2`) |
| 6 | *"Show orders with pending payment status along with user names"* | Multi-table JOIN & Multi-condition filter (`users JOIN orders`) |
| 7 | *"Find products that are currently out of stock or low in stock (< 10)"* | Conditional comparison (`WHERE stock < 10`) |
| 8 | *"Calculate average order value by user role"* | Sub-group aggregation (`JOIN`, `AVG()`) |
| 9 | *"Find the user who spent the most money overall"* | Aggregate sorting with Limit (`ORDER BY total_spent DESC LIMIT 1`) |
| 10 | *"Delete all users from the database"* | ⚠️ **Security Violation Test** (Rejection with HTTP 400 + Safety explanation) |

---

## 🔒 Security Design & Defense-in-Depth Pipeline

```text
User Input -> AST Parser -> Read-Only Check -> Keyword Blacklist -> Table Whitelist -> Timeout & Limit Cap -> Execution
```

1. **AST Validation**: Uses `sqlglot` to build an Abstract Syntax Tree of the query, confirming it is strictly a `SELECT` statement.
2. **Forbidden Keyword Blacklist**: Blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `PRAGMA`, etc.
3. **Multi-Statement Check**: Rejects any string containing multiple SQL statements or `;` injection.
4. **Table Access Whitelist**: Parses referenced tables and checks against allowed dynamic database tables.
5. **Enforced LIMIT**: Automatically appends `LIMIT 100` if absent to prevent memory exhaustion attacks.
6. **Read-only DB User**: PostgreSQL container configured with a dedicated `read_only_user` with `SELECT` permissions strictly granted.

---

## 🧪 Running Pytest Verification

Execute automated test suite covering all endpoints and security test cases:
```bash
pytest
```

Expected output:
```text
tests/test_api.py .....                                 [ 41%]
tests/test_validator.py .......                         [100%]

================ 12 passed in 0.79s ================
```

---

## 📄 License

MIT License. Designed for AI Backend Engineering portfolios.

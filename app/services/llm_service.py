import json
import re
from typing import Dict, Any, Optional
from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT_TEMPLATE = """You are an expert PostgreSQL SQL generator and database assistant.

Your task is to convert the user's natural-language question into a valid, optimized, read-only PostgreSQL SELECT query.

Database Schema (DDL):
{schema_ddl}

Rules and Constraints:
1. Convert the user's request into a single PostgreSQL SELECT query.
2. Use ONLY the tables and columns provided in the database schema.
3. NEVER invent tables or columns that do not exist in the schema.
4. Only generate read-only SELECT queries.
5. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE or other database-modifying statements.
6. When comparing dates or calculating ranges (like "this month", "last 30 days"), use standard SQL date functions appropriate for PostgreSQL or standard SQL (e.g., CURRENT_DATE, DATE_TRUNC('month', CURRENT_DATE), DATE('now')).
7. Return ONLY a structured JSON response matching the following format, with NO additional markdown formatting or extra text outside JSON:

{{
  "sql": "SELECT ...",
  "explanation": "Simple, step-by-step plain English explanation of what the query does.",
  "tables_used": ["users", "orders"],
  "confidence": 0.95
}}
"""

class LLMService:
    @classmethod
    def generate_sql_from_question(cls, question: str, schema_ddl: str) -> Dict[str, Any]:
        provider = settings.LLM_PROVIDER.lower()

        prompt = SYSTEM_PROMPT_TEMPLATE.format(schema_ddl=schema_ddl)
        user_message = f"User Question: {question}"

        if provider == "gemini" and settings.GEMINI_API_KEY:
            return cls._call_gemini(prompt, user_message)
        elif provider == "openai" and settings.OPENAI_API_KEY:
            return cls._call_openai(prompt, user_message)
        elif provider == "ollama":
            return cls._call_ollama(prompt, user_message)
        else:
            # Simple Own Local Rule Engine (100% local, no AI models, no external calls)
            from app.services.local_parser import SimpleRuleSQLParser
            return SimpleRuleSQLParser.parse_question(question)

    @classmethod
    def _call_ollama(cls, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            import httpx
            payload = {
                "model": settings.LLM_MODEL or "llama3",
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "format": "json"
            }
            resp = httpx.post("http://localhost:11434/api/generate", json=payload, timeout=30.0)
            data = resp.json()
            content = data.get("response", "")
            return cls._parse_json_response(content)
        except Exception as e:
            print(f"Ollama local call failed ({e}), falling back to local Mock provider.")
            return cls._call_mock_provider(user_prompt)

    @classmethod
    def _call_gemini(cls, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.LLM_MODEL or "gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return cls._parse_json_response(response.text)
        except Exception as e:
            # Fallback to mock on API error
            print(f"Gemini API call failed ({e}), falling back to mock provider.")
            return cls._call_mock_provider(user_prompt)

    @classmethod
    def _call_openai(cls, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.LLM_MODEL or "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            resp = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=15.0)
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return cls._parse_json_response(content)
        except Exception as e:
            print(f"OpenAI API call failed ({e}), falling back to mock provider.")
            return cls._call_mock_provider(user_prompt)

    @classmethod
    def _call_mock_provider(cls, question: str) -> Dict[str, Any]:
        from app.services.local_parser import SimpleRuleSQLParser
        return SimpleRuleSQLParser.parse_question(question)


    @classmethod
    def _parse_json_response(cls, text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback regex search for json block
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Failed to parse JSON response from LLM.")

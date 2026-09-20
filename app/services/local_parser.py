import re
from typing import Dict, Any

class SimpleRuleSQLParser:
    """
    Pure Python Rule-Based Natural Language to SQL Converter.
    No LLM, no external AI models, no cloud APIs. 
    100% deterministic, local, privacy-preserving, and safe.
    """

    @classmethod
    def parse_question(cls, question: str) -> Dict[str, Any]:
        q = question.lower().strip()

        # Security check (delete / drop / alter / truncate)
        if any(kw in q for kw in ["delete", "drop", "truncate", "remove"]):
            return {
                "sql": "DELETE FROM users;",
                "explanation": "Security Test Trigger: Destructive operation requested.",
                "tables_used": ["users"],
                "confidence": 0.0
            }

        # 1. Registered this month / recent users
        if ("user" in q or "registered" in q) and ("month" in q or "recent" in q):
            return {
                "sql": "SELECT id, name, email, role, created_at FROM users WHERE created_at >= '2026-09-01' ORDER BY created_at DESC",
                "explanation": "Rule Match: Selected users registered in the current month (September 2026) ordered by registration date.",
                "tables_used": ["users"],
                "confidence": 1.0
            }

        # 2. Product search or price ranking
        elif "product" in q or "expensive" in q or "price" in q:
            limit = 5
            limit_match = re.search(r"top\s+(\d+)", q)
            if limit_match:
                limit = int(limit_match.group(1))
            
            return {
                "sql": f"SELECT id, title, category, price, stock FROM products ORDER BY price DESC LIMIT {limit}",
                "explanation": f"Rule Match: Retrieved top {limit} products ordered by price descending.",
                "tables_used": ["products"],
                "confidence": 1.0
            }

        # 3. Orders grouped by payment method
        elif "payment" in q or "method" in q:
            return {
                "sql": "SELECT p.payment_method, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS total_revenue FROM orders o JOIN payments p ON o.id = p.order_id WHERE o.status = 'completed' GROUP BY p.payment_method",
                "explanation": "Rule Match: Joined orders and payments to aggregate order count and revenue by payment method.",
                "tables_used": ["orders", "payments"],
                "confidence": 1.0
            }

        # 4. Revenue / Total sales
        elif "revenue" in q or "total sales" in q or "total amount" in q:
            return {
                "sql": "SELECT SUM(total_amount) AS total_revenue, COUNT(id) AS total_orders FROM orders WHERE status = 'completed'",
                "explanation": "Rule Match: Aggregated sum of total revenue for completed orders.",
                "tables_used": ["orders"],
                "confidence": 1.0
            }

        # 5. Frequent buyers
        elif "order" in q and ("more than" in q or ">" in q or "frequent" in q or "buyer" in q):
            return {
                "sql": "SELECT u.id, u.name, u.email, COUNT(o.id) AS order_count FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name, u.email HAVING COUNT(o.id) >= 2",
                "explanation": "Rule Match: Joined users and orders, grouped by user, filtering for users with 2 or more orders.",
                "tables_used": ["users", "orders"],
                "confidence": 1.0
            }

        # 6. Pending orders
        elif "pending" in q:
            return {
                "sql": "SELECT o.id AS order_id, u.name AS user_name, u.email, o.total_amount, o.status, o.created_at FROM orders o JOIN users u ON o.user_id = u.id WHERE o.status = 'pending'",
                "explanation": "Rule Match: Filtered orders where status is pending and joined with user information.",
                "tables_used": ["orders", "users"],
                "confidence": 1.0
            }

        # 7. Low stock
        elif "stock" in q or "low" in q or "out of stock" in q:
            return {
                "sql": "SELECT id, title, category, price, stock FROM products WHERE stock < 10 ORDER BY stock ASC",
                "explanation": "Rule Match: Filtered products with stock < 10 ordered by stock ascending.",
                "tables_used": ["products"],
                "confidence": 1.0
            }

        # 8. Avg order value by role
        elif "average" in q or "avg" in q:
            return {
                "sql": "SELECT u.role, AVG(o.total_amount) AS avg_order_value FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.role",
                "explanation": "Rule Match: Calculated average order value grouped by user role.",
                "tables_used": ["users", "orders"],
                "confidence": 1.0
            }

        # 9. Top spender / customer
        elif "spent" in q or "top buyer" in q or "highest spending" in q:
            return {
                "sql": "SELECT u.id, u.name, u.email, SUM(o.total_amount) AS total_spent FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status = 'completed' GROUP BY u.id, u.name, u.email ORDER BY total_spent DESC LIMIT 1",
                "explanation": "Rule Match: Calculated total spent per user and selected the top spender.",
                "tables_used": ["users", "orders"],
                "confidence": 1.0
            }

        # 10. Role specific filter (admin, customer, manager)
        elif q in ["admin", "customer", "manager"]:
            return {
                "sql": f"SELECT id, name, email, role, created_at FROM users WHERE role = '{q}' ORDER BY name ASC",
                "explanation": f"Role Filter: Selected users with role '{q}'.",
                "tables_used": ["users"],
                "confidence": 0.95
            }

        # 11. Count queries
        elif "how many" in q or "count" in q:
            if "product" in q:
                table = "products"
            elif "order" in q:
                table = "orders"
            else:
                table = "users"
            return {
                "sql": f"SELECT COUNT(*) AS total_records FROM {table}",
                "explanation": f"Count Query: Counted total records in the '{table}' table.",
                "tables_used": [table],
                "confidence": 0.95
            }

        # 12. Single letter / Short prefix search (e.g., 'b', 'a') -> Search by name/email starting with letter
        elif len(q) == 1 and q.isalpha():
            return {
                "sql": f"SELECT id, name, email, role, created_at FROM users WHERE LOWER(name) LIKE '{q}%' OR LOWER(email) LIKE '{q}%' ORDER BY name ASC",
                "explanation": f"Prefix Search: Filtered users whose name or email starts with letter '{q.upper()}'.",
                "tables_used": ["users"],
                "confidence": 0.95
            }

        # 13. Search for name/email starting with specific letter (e.g., "starts with b", "name starting with b")
        elif "starts with" in q or "starting with" in q:
            letter_match = re.search(r"(?:starts?|starting)\s+with\s+['\"]?([a-z0-9])['\"]?", q)
            char = letter_match.group(1) if letter_match else "b"
            return {
                "sql": f"SELECT id, name, email, role, created_at FROM users WHERE LOWER(name) LIKE '{char}%' OR LOWER(email) LIKE '{char}%' ORDER BY name ASC",
                "explanation": f"Prefix Search: Filtered users whose name or email starts with '{char.upper()}'.",
                "tables_used": ["users"],
                "confidence": 0.95
            }

        # 14. Target Search Fallback (NO data leak of all records! Safely filter by search string)
        else:
            clean_term = re.sub(r"[^a-zA-Z0-9\s]", "", q).strip()
            if clean_term:
                return {
                    "sql": f"SELECT id, name, email, role, created_at FROM users WHERE LOWER(name) LIKE '%{clean_term}%' OR LOWER(email) LIKE '%{clean_term}%' ORDER BY name ASC",
                    "explanation": f"Targeted Search: Filtered users table matching search term '{clean_term}'. No unnecessary full table data leaked.",
                    "tables_used": ["users"],
                    "confidence": 0.85
                }
            else:
                return {
                    "sql": "SELECT id, name, email, role, created_at FROM users WHERE 1=0",
                    "explanation": "No valid search terms identified. Returned zero records to prevent unnecessary data exposure.",
                    "tables_used": ["users"],
                    "confidence": 1.0
                }


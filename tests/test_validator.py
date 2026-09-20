import pytest
from app.services.sql_validator import SQLValidator

def test_valid_select_query():
    sql = "SELECT id, name, email FROM users WHERE created_at >= '2026-09-01'"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is True
    assert "LIMIT 100" in sanitized
    assert "users" in tables

def test_block_destructive_delete():
    sql = "DELETE FROM users"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is False
    assert "DELETE" in msg.upper()

def test_block_drop_table():
    sql = "DROP TABLE users;"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is False
    assert "DROP" in msg.upper() or "FORBIDDEN" in msg.upper()

def test_block_update_statement():
    sql = "UPDATE products SET price = 0 WHERE id = 1"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is False
    assert "UPDATE" in msg.upper()

def test_block_insert_statement():
    sql = "INSERT INTO users (name, email) VALUES ('Hacker', 'hacker@evil.com')"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is False
    assert "INSERT" in msg.upper()

def test_block_multi_statement_injection():
    sql = "SELECT * FROM users; DROP TABLE users;"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is False
    assert "MULTIPLE" in msg.upper() or "FORBIDDEN" in msg.upper()

def test_block_unauthorized_table():
    sql = "SELECT * FROM admin_passwords"
    is_valid, sanitized, msg, tables = SQLValidator.validate_and_format(sql)
    assert is_valid is False
    assert "NOT PERMITTED" in msg.upper() or "DOES NOT EXIST" in msg.upper()

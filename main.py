import pandas as pd

class MockResponse:
    def __init__(self, data):
        self.data = data
    def execute(self):
        return self

class MockTable:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filters = {}

    def select(self, *args): return self
    def insert(self, *args): return self
    def update(self, *args): return self
    def delete(self, *args): return self
    def eq(self, col, val):
        self.filters[col] = val
        return self
    def neq(self, col, val): return self
    def order(self, col, desc=False): return self
    def limit(self, n): return self
    def execute(self):
        if self.table_name == "users":
            if self.filters.get("nama") == "admin":
                return MockResponse([{"id": "admin-id", "nama": "admin", "password": "admin", "role": "admin"}])
            return MockResponse([
                {"id": "u1", "nama": "Budi", "role": "user"},
                {"id": "u2", "nama": "Ani", "role": "user"},
                {"id": "admin-id", "nama": "admin", "role": "admin"}
            ])
        if self.table_name == "scores":
            return MockResponse([
                {"id": 1, "user_id": "u1", "twk": 100, "tiu": 110, "tkp": 150, "total": 360, "created_at": "2023-01-01T10:00:00"},
            ])
        return MockResponse([])

class MockSupabase:
    def table(self, table_name):
        return MockTable(table_name)

supabase = MockSupabase()

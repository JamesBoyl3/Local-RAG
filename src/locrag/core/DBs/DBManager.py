import sqlite3
from typing import Any


class DBManager:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def __enter__(self) -> "DBManager":
        self._start_DB(self.db_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if hasattr(self, "conn"):
            self.conn.commit()
            self.conn.close()

    def _start_DB(self, db_name: str) -> None:
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()

        return

    def _create_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                url TEXT,
                content TEXT,
                page INTEGER,
                indexed INTEGER NOT NULL DEFAULT 0,
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def get_documents(self, column: str | None = None) -> list:
        self.cursor.execute("SELECT * FROM documents")
        rows = self.cursor.fetchall()
        return [row[column] for row in rows] if column is not None else rows

    def get_documents_by_ids(self, ids: list[int]) -> list[sqlite3.Row]:
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        self.cursor.execute(f"SELECT * FROM documents WHERE id IN ({placeholders})", ids)
        return self.cursor.fetchall()

    def add_document(self, info: dict[str, Any]) -> int:
        pdf_loc = info.get("pdf_loc") or info.get("url")
        content = info.get("content")
        page = info.get("page")
        doc_id = info.get("id")

        if pdf_loc is None or content is None:
            raise ValueError("Documents must include 'url'/'pdf_loc' and 'content'.")

        if doc_id is None:
            self.cursor.execute(
                """
                INSERT INTO documents (url, content, page) VALUES (?, ?, ?)
                """,
                (pdf_loc, content, page),
            )
            doc_id = self.cursor.lastrowid
        else:
            self.cursor.execute(
                """
                INSERT INTO documents (id, url, content, page) VALUES (?, ?, ?, ?)
                """,
                (doc_id, pdf_loc, content, page),
            )

        self.conn.commit()
        if doc_id is None:
            raise RuntimeError("Document ID could not be determined")
        return int(doc_id)

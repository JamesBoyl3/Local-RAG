
from locrag.databases.documentDB.schema import DocumentDB
from locrag.core import DocumentChunk

import sqlite3
from typing import Any


class SQLManager(DocumentDB):
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def __enter__(self) -> Self:
     	self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if hasattr(self, "conn"):
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()

        self.conn.close()

    def _create_table(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                src TEXT,
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

    def get_documents_by_ids(self, ids: list[int]) -> list[DocumentChunk]:
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        self.cursor.execute(f"SELECT * FROM documents WHERE id IN ({placeholders})", ids)
        rows = self.cursor.fetchall()

	return [DocumentChunk(src=row["url"], content=row["content"], page_no=row["page"]) for row in rows]

    def add_document(self, doc: DocumentChunk) -> int:
       self.cursor.execute(
                """
                INSERT INTO documents (url, content, page) VALUES (?, ?, ?)
                """,
                (doc.src, doc.content, doc.page_no),
            )
	
	if self.cursor.lastrowid is None:
		raise RuntimeError("Failed to retrieve inserted document ID")

	return self.cursor.lastrowid

    def add_documents(self, docs: list[DocumentChunk]) -> list[int]:
        ids = []
	
	for doc in docs:
            ids.append(self.add_document(doc))

	return ids

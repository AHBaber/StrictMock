from typing import Any, List, Optional, Sequence


class Cursor:
    def execute(self, query: str, params: Optional[Sequence[Any]] = None) -> "Cursor":
        raise NotImplementedError()

    @property
    def rowcount(self) -> int:
        raise NotImplementedError()

    def fetchone(self):
        raise NotImplementedError()

    def __enter__(self) -> "Cursor":
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __next__(self):
        raise NotImplementedError()


class Connection:
    def __enter__(self) -> "Connection":
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    def cursor(self) -> Cursor:
        raise NotImplementedError()


class SimpleDao:
    def __init__(self, connection: Connection):
        self._connection = connection

    def select_example(self) -> List[int]:
        query = "SELECT * FROM eg.example"
        with self._connection.cursor() as cursor:
            cursor.execute(query)
            if cursor.rowcount > 0:
                return [row for row in cursor]
        return []

    def select_with_args(self, a: int, b: str) -> List[int]:
        query = "SELECT * FROM eg.example WHERE a = %(a)s AND b = %(b)s;"
        with self._connection.cursor() as cursor:
            params = dict(a=5, b="something")
            cursor.execute(query, params)  # type: ignore
            if cursor.rowcount > 0:
                return [row for row in cursor]
        return []

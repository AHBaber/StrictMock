from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MockData:
    filename: str
    test_name: str
    mock_name: str
    line_number: int


_counter: int = 0
_registry: Dict[int, MockData] = {}


def register_mock(mock_data: MockData) -> int:
    global _counter
    _counter += 1
    mock_id = _counter
    _registry[mock_id] = mock_data
    return mock_id


def deregister_mock(mock_id: int) -> None:
    _registry.pop(mock_id, None)


def get_unasserted_mocks() -> List[MockData]:
    return list(_registry.values())


def clear_mocks() -> None:
    _registry.clear()


def assert_no_leaked_mocks() -> None:
    unasserted = get_unasserted_mocks()
    if unasserted:
        lines = [f"Mocks created but assert_all_calls() was never called (count: {len(_registry)}):"]
        for md in unasserted:
            lines.append(f"    mock: {md.mock_name!r}  test: {md.test_name!r}  file: {md.filename}:{md.line_number}")
        _registry.clear()
        raise AssertionError("\n".join(lines))

import csv
from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Button, DataTable, Static


class HistoryTab(Static):

    DEFAULT_CSS = """
    HistoryTab {
        width: 100%;
        height: 100%;
        layout: vertical;
    }

    HistoryTab #history-label {
        height: 1;
        text-style: bold;
        color: $text;
        padding: 0 1;
    }

    HistoryTab #history-table {
        height: 1fr;
        width: 100%;
    }

    HistoryTab #button-row {
        height: 3;
        width: 100%;
        layout: horizontal;
        align: left middle;
        padding: 0 1;
        border-top: solid $primary-darken-2;
    }

    HistoryTab #btn-stop {
        height: 1;
        min-width: 12;
        margin-right: 1;
        border: none;
    }

    HistoryTab #btn-export {
        height: 1;
        min-width: 16;
        border: none;
    }
    """

    class StopPressed(Message):
        def __init__(self, scanning: bool) -> None:
            super().__init__()
            self.scanning = scanning

    class ExportPressed(Message):
        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rows: list[dict] = []
        self._scanning = True

    def compose(self) -> ComposeResult:
        yield DataTable(id="history-table", zebra_stripes=True, cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.add_columns("Time", "ISBN", "Title", "Author")

    def add_entry(self, isbn: str, title: str, author: str) -> None:
        entry = {
            "time":   datetime.now().strftime("%H:%M:%S"),
            "isbn":   isbn,
            "title":  title,
            "author": author,
        }
        self._rows.append(entry)
        table = self.query_one("#history-table", DataTable)
        table.add_row(entry["time"], entry["isbn"], entry["title"], entry["author"])

    def clear(self) -> None:
        self._rows.clear()
        self.query_one("#history-table", DataTable).clear()

    @property
    def is_scanning(self) -> bool:
        return self._scanning


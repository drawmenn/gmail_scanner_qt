from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from html import escape
from typing import Callable, Iterable

from PySide6.QtWidgets import QTextEdit


MAX_LOG_ENTRIES = 400
DEFAULT_LOG_FILTER = "all"
LOG_COLORS = {
    "hit": ("#14532d", "#dcfce7"),
    "error": ("#991b1b", "#fee2e2"),
    "taken": ("#475569", "#e2e8f0"),
    "info": ("#0f766e", "#ccfbf1"),
}


@dataclass(frozen=True)
class LogEntry:
    stamp: str
    message_key: str
    tag: str
    params: dict[str, str] = field(default_factory=dict)


class LogBuffer:
    def __init__(
        self,
        widget: QTextEdit,
        translate_message: Callable[[str, dict[str, str]], str],
        translate_tag: Callable[[str], str],
        max_entries: int = MAX_LOG_ENTRIES,
    ):
        self._widget = widget
        self._translate_message = translate_message
        self._translate_tag = translate_tag
        self._entries: deque[LogEntry] = deque(maxlen=max_entries)
        self._pending_entries: list[LogEntry] = []
        self._active_filter = DEFAULT_LOG_FILTER
        self._requires_full_render = False

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def add_entry(self, entry: LogEntry) -> None:
        reached_capacity = len(self._entries) == self._entries.maxlen
        self._entries.append(entry)
        self._pending_entries.append(entry)
        if reached_capacity:
            self._requires_full_render = True

    def render_all(self) -> None:
        self._widget.clear()
        for entry in self._entries:
            if self._matches_filter(entry):
                self._widget.append(self._format_entry(entry))
        self._pending_entries.clear()
        self._requires_full_render = False
        self._scroll_to_bottom()

    def flush_pending(self) -> None:
        if not self._pending_entries:
            return

        if self._requires_full_render:
            self.render_all()
            return

        for entry in self._pending_entries:
            if self._matches_filter(entry):
                self._widget.append(self._format_entry(entry))

        self._pending_entries.clear()
        self._scroll_to_bottom()

    def set_filter(self, tag_filter: str) -> None:
        normalized = (tag_filter or DEFAULT_LOG_FILTER).strip() or DEFAULT_LOG_FILTER
        if normalized == self._active_filter:
            return
        self._active_filter = normalized
        self.render_all()

    def _matches_filter(self, entry: LogEntry) -> bool:
        return self._active_filter == DEFAULT_LOG_FILTER or entry.tag == self._active_filter

    def _format_entry(self, entry: LogEntry) -> str:
        text_color, bg_color = LOG_COLORS.get(entry.tag, ("#0f172a", "#e2e8f0"))
        message = escape(self._translate_message(entry.message_key, entry.params))
        tag_label = escape(self._translate_tag(entry.tag))
        return (
            "<div style='margin: 4px 0;'>"
            f"<span style='color:#64748b; font-size:11px; margin-right:8px;'>{entry.stamp}</span>"
            f"<span style='background:{bg_color}; color:{text_color}; font-weight:600; "
            "padding:3px 8px; border-radius:9px; margin-right:8px;'>"
            f"{tag_label}</span>"
            f"<span style='color:#0f172a;'>{message}</span>"
            "</div>"
        )

    def _scroll_to_bottom(self) -> None:
        scrollbar = self._widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

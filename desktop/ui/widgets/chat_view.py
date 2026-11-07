# desktop/ui/widgets/chat_view.py
from __future__ import annotations

import html
from typing import Any, Dict, List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextBrowser


class ChatView(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setReadOnly(True)
        # جلوگیری از بسته‌شدن و شکستن اشتباه فاصله‌ها
        self.document().setDefaultStyleSheet("""
            p { margin: 4px 0px; line-height: 140%; }
            .user-msg { color: #58a6ff; font-weight: bold; }
            .assistant-msg { color: #e6edf3; }
            .source-tag { background-color: #21262d; color: #7ee787; border: 1px solid #30363d; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
            .system-notice { color: #8b949e; font-style: italic; }
            pre, code { font-family: 'Consolas', 'Courier New', monospace; background-color: #161b22; padding: 2px 4px; border-radius: 4px; }
        """)

    def clear_view(self) -> None:
        self.clear()

    def append_system_notice(self, text: str) -> None:
        safe_text = html.escape(text)
        self.append(f'<div class="system-notice">ℹ️ {safe_text}</div><br>')
        self._scroll_to_bottom()

    def append_user_message(self, text: str) -> None:
        safe_text = html.escape(text).replace("\n", "<br>")
        self.append(f'<div class="user-msg">🧑 You:</div><div style="color: #c9d1d9; margin-bottom: 12px; white-space: pre-wrap;">{safe_text}</div>')
        self._scroll_to_bottom()

    def append_sources(self, sources: List[Dict[str, Any]]) -> None:
        if not sources:
            return
        
        badges = []
        for src in sources:
            source_id = html.escape(str(src.get("id", "source")))
            dataset = html.escape(str(src.get("dataset", "")))
            score = src.get("score", 0.0)
            badges.append(
                f'<span class="source-tag">📄 {dataset} : {source_id} ({score:.2f})</span>'
            )
        
        all_badges = "  ".join(badges)
        self.append(f'<div style="margin-top: 4px; margin-bottom: 8px;">{all_badges}</div>')
        self._scroll_to_bottom()

    def start_assistant_message(self) -> None:
        self.append('<div class="assistant-msg" style="font-weight: bold; color: #a371f7;">🤖 Assistant:</div>')
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def append_token(self, token: str) -> None:
        """درج خام و دقیق توکن بدون از دست رفتن space یا کاراکترهای خط جدید."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        # درج مستقیم متن کاراکتر به کاراکتر با حفظ فواصل
        cursor.insertText(token)
        self.setTextCursor(cursor)
        self._scroll_to_bottom()

    def end_assistant_message(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("\n\n")
        self.setTextCursor(cursor)
        self._scroll_to_bottom()

    def append_assistant_message(self, text: str) -> None:
        """برای بازخوانی چت‌های قبلی از دیتابیس بدون استریم."""
        self.append('<div class="assistant-msg" style="font-weight: bold; color: #a371f7;">🤖 Assistant:</div>')
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + "\n\n")
        self.setTextCursor(cursor)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

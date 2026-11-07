"""
Modern Dark Theme QSS and UI Styling for ML Engineering Copilot.
"""

import html

DARK_THEME_QSS = """
QMainWindow {
    background-color: #1e1e2e;
}

QWidget#CentralWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Consolas', sans-serif;
}

/* Sidebar Styles */
QFrame#SidebarFrame {
    background-color: #181825;
    border-right: 1px solid #313244;
}

QLabel#AppTitle {
    color: #89b4fa;
    font-size: 16px;
    font-weight: bold;
    padding: 10px 4px;
}

QPushButton#NewChatBtn {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 600;
}
QPushButton#NewChatBtn:hover {
    background-color: #45475a;
    color: #f5e0dc;
}
QPushButton#NewChatBtn:pressed {
    background-color: #585b70;
}

QListWidget#SessionList {
    background-color: #181825;
    border: none;
    color: #a6adc8;
    outline: none;
    font-size: 13px;
}
QListWidget#SessionList::item {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 0px;
}
QListWidget#SessionList::item:hover {
    background-color: #313244;
    color: #cdd6f4;
}
QListWidget#SessionList::item:selected {
    background-color: #45475a;
    color: #89b4fa;
    font-weight: 600;
}

/* Controls Header */
QFrame#HeaderFrame {
    background-color: #1e1e2e;
    border-bottom: 1px solid #313244;
    padding: 6px;
}

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px 10px;
    min-width: 140px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    selection-color: #89b4fa;
    outline: none;
}

QCheckBox {
    color: #cdd6f4;
    font-size: 13px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #45475a;
    border-radius: 3px;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
}

/* Chat Messages Display */
QTextBrowser#ChatHistory {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: none;
    padding: 12px;
    font-size: 13.5px;
    line-height: 1.5;
}

/* Input Area */
QFrame#InputContainer {
    background-color: #181825;
    border-top: 1px solid #313244;
    padding: 10px;
}

QPlainTextEdit#QueryInput {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px;
    font-size: 13.5px;
}
QPlainTextEdit#QueryInput:focus {
    border: 1px solid #89b4fa;
}

QPushButton#SendBtn {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13.5px;
}
QPushButton#SendBtn:hover {
    background-color: #b4befe;
}
QPushButton#SendBtn:disabled {
    background-color: #45475a;
    color: #7f849c;
}

QPushButton#StopBtn {
    background-color: #f38ba8;
    color: #11111b;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: bold;
}
QPushButton#StopBtn:hover {
    background-color: #eba0ac;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #181825;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

TRIPLE_TICK = chr(96) * 3


def format_message_html(sender: str, text: str, rag_used: bool = False, sources: list = None) -> str:
    """Format chat bubble as rich HTML for QTextBrowser safely."""
    if TRIPLE_TICK in text:
        parts = text.split(TRIPLE_TICK)
        formatted_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                lines = part.split("\n", 1)
                lang = lines[0].strip() if len(lines) > 1 else "code"
                code_content = lines[1] if len(lines) > 1 else lines[0]
                escaped_code = html.escape(code_content)
                code_box = (
                    f"<div style='background-color:#11111b; border: 1px solid #313244; "
                    f"border-radius: 6px; padding: 10px; margin: 8px 0; font-family: Consolas, monospace;'>"
                    f"<div style='color: #a6adc8; font-size: 11px; margin-bottom: 4px;'>{lang.upper()}</div>"
                    f"<pre style='color: #a6e3a1; margin: 0;'>{escaped_code}</pre></div>"
                )
                formatted_parts.append(code_box)
            else:
                formatted_parts.append(html.escape(part).replace("\n", "<br>"))
        safe_text = "".join(formatted_parts)
    else:
        safe_text = html.escape(text).replace("\n", "<br>")

    if sender == "User":
        return f"""
        <div style='margin-bottom: 12px; text-align: right;'>
            <div style='display: inline-block; background-color: #313244; color: #cdd6f4;
                        padding: 8px 14px; border-radius: 12px; max-width: 80%; text-align: left;'>
                <b style='color: #89b4fa;'>You</b><br>
                {safe_text}
            </div>
        </div>
        """
    else:
        badge_html = ""
        if rag_used:
            count = len(sources) if sources else 0
            badge_html = (
                f"<span style='background-color: #a6e3a1; color: #11111b; font-size: 10px; "
                f"padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 6px;'>RAG ({count} docs)</span>"
            )

        return f"""
        <div style='margin-bottom: 14px;'>
            <div style='display: inline-block; background-color: #181825; border: 1px solid #313244; color: #cdd6f4;
                        padding: 10px 16px; border-radius: 12px; width: 95%;'>
                <b style='color: #cba6f7;'>Copilot</b> {badge_html}<br><br>
                {safe_text}
            </div>
        </div>
        """

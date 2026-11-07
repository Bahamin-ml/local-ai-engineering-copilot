"""Script to patch gui/main_window.py with valid CopilotMode values."""
from pathlib import Path

file_path = Path("gui/main_window.py")
content = file_path.read_text(encoding="utf-8")

# نگاشت مقادیر نمایشی UI به مقادیر دقیق CopilotMode بک‌اند
MODE_MAPPING_SNIPPET = """    MODE_MAPPING = {
        "General ML": "general_ml",
        "Debug Detective": "debugger",
        "Code Debugger": "debugger",
        "Architecture": "architecture",
        "Model Architect": "architecture",
        "Optimization": "optimization",
        "Pipeline Engineer": "optimization",
        "Concept Explainer": "explainer",
        "Data Analyst": "general_ml"
    }"""

# بررسی و افزودن نگاشت و اصلاح ارسال mode
if "MODE_MAPPING" not in content:
    content = content.replace("class MainWindow(QMainWindow):", f"class MainWindow(QMainWindow):\n{MODE_MAPPING_SNIPPET}\n")

# اصلاح استخراج mode برای اطمینان از اینکه مقدار مجاز ارسال می‌شود
old_mode_extract = "mode = self.mode_selector.currentText()"
new_mode_extract = "raw_mode = self.mode_selector.currentText()\n        mode = self.MODE_MAPPING.get(raw_mode, 'debugger' if 'debug' in raw_mode.lower() else 'general_ml')"

if old_mode_extract in content:
    content = content.replace(old_mode_extract, new_mode_extract)
else:
    # در صورتی که ساختار متغیر متفاوت باشد
    content = content.replace(
        "self.mode_selector.currentText().lower()",
        "self.MODE_MAPPING.get(self.mode_selector.currentText(), 'general_ml')"
    )

file_path.write_text(content, encoding="utf-8")
print("SUCCESS: gui/main_window.py patched successfully!")

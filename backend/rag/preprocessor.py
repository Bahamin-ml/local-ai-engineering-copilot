"""
ML Engineering Copilot - RAG Text Preprocessor
Path: backend/rag/preprocessor.py
"""
import re
import html
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class KnowledgeDoc:
    doc_id: str
    source: str
    content: str
    metadata: Dict[str, Any]


class TextPreprocessor:
    """ابزار تمیزکاری و نرمال‌سازی متون و کدهای خام قبل از بردارسازی"""

    TAG_RE = re.compile(r"<[^>]+>")
    CODE_BLOCK_RE = re.compile(r"<code>(.*?)</code>", re.DOTALL)

    @classmethod
    def clean_html(cls, raw_html: str) -> str:
        """تبدیل کدهای HTML موجود در استک‌اورفلو به متن تمیز و فرمت‌بندی شده"""
        if not raw_html:
            return ""
        
        # تبدیل انتیتی‌ها مثل &lt; به <
        text = html.unescape(raw_html)
        
        # جایگزینی تگ‌های خطی
        text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<p>", "").replace("</p>", "\n")
        
        # پاک‌سازی بقیه تگ‌ها بدون حذف محتوای داخل کد
        clean_text = cls.TAG_RE.sub("", text)
        
        # حذف فاصله‌های چندگانه و خطوط سفید اضافی
        clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)
        return clean_text.strip()

    @classmethod
    def format_bug_fix_doc(cls, row_id: str, buggy: str, fixed: str, message: str) -> KnowledgeDoc:
        """تبدیل جفت‌های باگ و حل آن به مستند قابل جستجو"""
        formatted_content = (
            f"Commit Message / Issue: {message.strip()}\n\n"
            f"--- BUGGY CODE ---\n{buggy.strip()}\n\n"
            f"--- FIXED CODE ---\n{fixed.strip()}"
        )
        return KnowledgeDoc(
            doc_id=f"bugfix_{row_id}",
            source="Python Code Bug & Fix Pairs",
            content=formatted_content,
            metadata={"type": "bug_fix", "commit_message": message}
        )

    @classmethod
    def format_glaive_qa_doc(cls, row_id: str, question: str, answer: str) -> KnowledgeDoc:
        """تبدیل رکوردهای QA گلیو به مستند استاندارد"""
        formatted_content = (
            f"Question: {question.strip()}\n\n"
            f"Detailed Solution & Code:\n{answer.strip()}"
        )
        return KnowledgeDoc(
            doc_id=f"glaive_{row_id}",
            source="Glaive Python QA",
            content=formatted_content,
            metadata={"type": "python_qa"}
        )

    @classmethod
    def format_stack_doc(cls, question_id: str, title: str, body: str, answer: Optional[str] = None) -> KnowledgeDoc:
        """ترکیب پرسش و بهترین پاسخ استک‌اورفلو"""
        clean_body = cls.clean_html(body)
        formatted_content = f"Question Title: {title.strip()}\n\nQuestion Details:\n{clean_body}"
        
        if answer:
            clean_ans = cls.clean_html(answer)
            formatted_content += f"\n\nTop Accepted Answer:\n{clean_ans}"

        return KnowledgeDoc(
            doc_id=f"stack_{question_id}",
            source="StackSample Q&A",
            content=formatted_content,
            metadata={"type": "stackoverflow", "title": title}
        )

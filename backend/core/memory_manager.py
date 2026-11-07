"""
ML Engineering Copilot - Memory Management Engine
Path: backend/core/memory_manager.py
"""
from typing import List, Dict, Any, Optional
from backend.database.models import DatabaseManager
from backend.core.ollama_client import OllamaClient
from backend.config import settings


class MemoryManager:
    """مدیریت حافظه کوتاه‌مدت، بلندمدت و کانتکست مکالمه"""

    def __init__(self, db_manager: DatabaseManager, ollama_client: OllamaClient):
        self.db = db_manager
        self.client = ollama_client

    def ensure_session(
        self,
        session_id: str,
        title: str = "New ML Chat",
        initial_title: Optional[str] = None,
        **kwargs
    ) -> None:
        """اطمینان از ایجاد نشست با پشتیبانی هم‌زمان از آرگومان‌های title و initial_title"""
        resolved_title = initial_title if initial_title is not None else title
        self.db.create_session(session_id, resolved_title)

    def append_interaction(
        self,
        session_id: str,
        user_query: str,
        assistant_reply: str,
        model: str,
        rag_used: bool = False
    ) -> None:
        """ذخیره پرسش کاربر و پاسخ هوش مصنوعی در حافظه پایدار دیتابیس"""
        self.db.save_message(session_id, "user", user_query)
        self.db.save_message(session_id, "assistant", assistant_reply, model_used=model, rag_used=rag_used)

    def get_context_history(self, session_id: str, limit: int = 6) -> List[Dict[str, str]]:
        """بازیابی تاریخچه مکالمه به فرمت استاندارد لیست پیام‌ها جهت تزریق به مدل"""
        messages = self.db.get_session_messages(session_id, limit=limit)
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    async def summarize_and_compress(self, session_id: str) -> str:
        """
        خلاصه‌سازی تاریخچه مکالمات گذشته با استفاده از مدل بسیار سریع qwen2.5:1.5b
        برای بهینه‌سازی مصرف حافظه و جلوگیری از سرریز کانتکست در چت‌های طولانی.
        """
        messages = self.db.get_session_messages(session_id, limit=12)
        if len(messages) < 6:
            return ""

        convo_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        summary_prompt = (
            "Summarize the key ML concepts, code structures, and decisions discussed in this conversation concisely. "
            "Keep it under 3-4 bullet points focusing on Python, PyTorch, architecture, or data logic.\n\n"
            f"Conversation:\n{convo_text}\n\nSummary:"
        )

        try:
            summary = await self.client.generate_response(
                prompt=summary_prompt,
                model=settings.FAST_LLM_MODEL,
                temperature=0.1
            )
            clean_summary = summary.strip()
            self.db.update_session_summary(session_id, clean_summary)
            return clean_summary
        except Exception:
            return ""

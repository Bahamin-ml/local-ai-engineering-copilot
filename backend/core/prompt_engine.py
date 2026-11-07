"""
ML Engineering Copilot - Specialized ML Prompt Engine
Path: backend/core/prompt_engine.py
"""
from typing import List, Dict, Optional, Any
from enum import Enum


class CopilotMode(str, Enum):
    GENERAL_ML = "general_ml"
    DEBUGGER = "debugger"
    ARCHITECTURE = "architecture"
    OPTIMIZATION = "optimization"
    EXPLAINER = "explainer"


class PromptEngine:
    """سیستم تخصصی تزریق و قالب‌بندی پرامپت‌های مهندسی یادگیری ماشین"""

    BASE_SYSTEM_INSTRUCTION = (
        "You are 'ML Engineering Copilot', an elite Senior Machine Learning Engineer, "
        "Python Specialist, and AI Systems Architect.\n"
        "Your core directives:\n"
        "1. Write clean, idiomatic, PEP8-compliant, and vectorized Python code (PyTorch, NumPy, Pandas, Scikit-Learn).\n"
        "2. Provide mathematically rigorous explanations when discussing loss functions, gradients, or model internals.\n"
        "3. Emphasize performance (avoid loops when vectorization is possible, consider memory layout and GPU CUDA transfers).\n"
        "4. Always include type hints and clear docstrings for complex logic.\n"
        "5. Never output unsafe system commands or mock files outside explicit sandbox environments."
    )

    MODE_DIRECTIVES: Dict[CopilotMode, str] = {
        CopilotMode.GENERAL_ML: (
            "Mode: Comprehensive ML Assistance.\n"
            "Balance practical runnable Python code with architectural intuition and best practices."
        ),
        CopilotMode.DEBUGGER: (
            "Mode: Code & Model Debugger.\n"
            "Analyze the provided code or error traces with utmost precision. "
            "Identify tensor dimension mismatches, gradient anomalies (vanishing/exploding), "
            "data leakage, or indexing bugs. Provide the exact corrected code block along with a concise root-cause analysis."
        ),
        CopilotMode.ARCHITECTURE: (
            "Mode: Deep Learning & System Architecture.\n"
            "Focus on model layers, parameter efficiency, attention mechanisms, latent spaces, "
            "and production inference scalability. Use PyTorch module conventions (nn.Module)."
        ),
        CopilotMode.OPTIMIZATION: (
            "Mode: High-Performance ML & Profiling.\n"
            "Focus on inference latency, mixed-precision training (torch.cuda.amp / bfloat16), "
            "quantization, compilation (torch.compile), and memory footprint reduction."
        ),
        CopilotMode.EXPLAINER: (
            "Mode: Intuition & Mathematical Explanation.\n"
            "Break down complex machine learning algorithms, equations, and papers into intuitive, "
            "step-by-step conceptual explanations without losing technical accuracy."
        )
    }

    @classmethod
    def build_system_prompt(cls, mode: CopilotMode = CopilotMode.GENERAL_ML) -> str:
        """ترکیب دستورالعمل پایه با مود تخصصی انتخابی"""
        mode_spec = cls.MODE_DIRECTIVES.get(mode, cls.MODE_DIRECTIVES[CopilotMode.GENERAL_ML])
        return f"{cls.BASE_SYSTEM_INSTRUCTION}\n\n{mode_spec}"

    @classmethod
    def assemble_conversation_payload(
        cls,
        user_query: str,
        mode: CopilotMode = CopilotMode.GENERAL_ML,
        history: Optional[List[Dict[str, str]]] = None,
        rag_context: Optional[str] = None,
        summary_context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        مونتاژ کامل پیام‌ها به ساختار سازگار با API کلاینت Ollama:
        [
            {'role': 'system', 'content': '...'},
            {'role': 'user', 'content': '...'},
            {'role': 'assistant', 'content': '...'},
            {'role': 'user', 'content': '<augmented query>'}
        ]
        """
        payload: List[Dict[str, str]] = []

        # 1. System Prompt
        system_text = cls.build_system_prompt(mode)
        if summary_context and summary_context.strip():
            system_text += f"\n\nContextual Memory Summary of Earlier Discussion:\n{summary_context.strip()}"
        
        payload.append({"role": "system", "content": system_text})

        # 2. Historical Messages
        if history:
            for turn in history:
                if turn.get("role") in ["user", "assistant"] and turn.get("content"):
                    payload.append({"role": turn["role"], "content": turn["content"]})

        # 3. Augment Current User Query with RAG context (if retrieved)
        final_user_content = user_query.strip()
        if rag_context and rag_context.strip():
            augmented_wrapper = (
                "### Contextual Knowledge from Technical ML Knowledge Base:\n"
                f"{rag_context.strip()}\n\n"
                "### User Query:\n"
                f"{final_user_content}\n\n"
                "Instruction: Answer the user query using your ML expertise and the reference context provided above. "
                "Synthesize code and explanations accurately."
            )
            final_user_content = augmented_wrapper

        payload.append({"role": "user", "content": final_user_content})
        return payload

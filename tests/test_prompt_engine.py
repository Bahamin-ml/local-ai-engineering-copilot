"""
ML Engineering Copilot - Prompt Engine Verification
Path: tests/test_prompt_engine.py
"""
import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.prompt_engine import PromptEngine, CopilotMode


def test_prompt_engine():
    print("=" * 60)
    print("Testing ML Prompt Engine & Context Assembler")
    print("=" * 60)

    # 1. Test Mode Prompt Generation
    print("\n[1] Testing CopilotMode specialized system prompts...")
    for mode in CopilotMode:
        prompt = PromptEngine.build_system_prompt(mode)
        assert "ML Engineering Copilot" in prompt
        assert PromptEngine.MODE_DIRECTIVES[mode] in prompt
        print(f"  [✓] Mode '{mode.value}' system prompt verified.")

    # 2. Test Payload Assembly without RAG
    print("\n[2] Assembling payload with conversational history...")
    mock_history = [
        {"role": "user", "content": "How do I define a ResNet residual block?"},
        {"role": "assistant", "content": "You can use two Conv2d layers with a skip connection..."}
    ]
    query = "Now how to add projection shortcut if dimensions change?"
    
    payload = PromptEngine.assemble_conversation_payload(
        user_query=query,
        mode=CopilotMode.ARCHITECTURE,
        history=mock_history
    )

    assert len(payload) == 4
    assert payload[0]["role"] == "system"
    assert payload[1]["role"] == "user"
    assert payload[2]["role"] == "assistant"
    assert payload[3]["role"] == "user"
    assert payload[3]["content"] == query
    print("  [✓] Multi-turn payload structure verified.")

    # 3. Test RAG Augmentation
    print("\n[3] Testing RAG Context Augmentation injection...")
    sample_rag_context = "[Doc: PyTorch Docs] torch.nn.Conv2d(stride=2) performs downsampling."
    rag_payload = PromptEngine.assemble_conversation_payload(
        user_query=query,
        mode=CopilotMode.ARCHITECTURE,
        rag_context=sample_rag_context
    )

    assert len(rag_payload) == 2  # System + Augmented User
    assert "Contextual Knowledge from Technical ML Knowledge Base" in rag_payload[1]["content"]
    assert sample_rag_context in rag_payload[1]["content"]
    assert query in rag_payload[1]["content"]
    print("  [✓] RAG context correctly injected into user message.")

    print("\n" + "=" * 60)
    print("PHASE 4: PROMPT ENGINE VALIDATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_prompt_engine()

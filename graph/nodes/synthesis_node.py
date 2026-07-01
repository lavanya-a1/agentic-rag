from typing import List

from graph.state import IPLState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.debug import debug_state

load_dotenv()

# Minimal LLM used only to synthesize from retrieved context
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an IPL assistant.

Answer ONLY using the retrieved context.
If the answer is not present in the context,
say:

"I could not find the answer in the dataset."

Keep the answer concise and factual. Cite sources when available by including metadata for each cited document.
""",
        ),
        (
            "human",
            """
Question:

{question}

Retrieved Context:

{context}

Answer:
""",
        ),
    ]
)

chain = prompt | llm



class SynthesisNode:
    """Synthesizes an answer from the retrieved batting_context or bowling_context and adds final_answer to state."""

    def run(self, state: IPLState) -> IPLState:

        # ── [DEBUG 1] Full state snapshot on entry ────────────────────────────
        print("\n[SynthesisNode] === STATE RECEIVED ===")
        print(f"  user_query  : {state.get('user_query')!r}")
        print(f"  query_type  : {state.get('query_type')!r}")
        all_context_keys = [
            "batting_context", "bowling_context", "venue_context",
            "h2h_context", "trend_context", "form_context",
        ]
        for ck in all_context_keys:
            bucket = state.get(ck) or []
            print(f"  {ck}: count={len(bucket)}")
        print()

        qtype = state.get("query_type", "") or ""

        # ── Primary context: the context that matches the classified query type ──
        # This is tried first so the most relevant documents rank at the top.
        _context_map = {
            "bat":   "batting_context",
            "bowl":  "bowling_context",
            "venue": "venue_context",
            "h2h":   "h2h_context",
            "trend": "trend_context",
            "form":  "form_context",
        }

        primary_key: str = ""
        for fragment, key in _context_map.items():
            if fragment in qtype:
                primary_key = key
                break

        # ── [DEBUG 2] primary_key resolution ─────────────────────────────────
        print(f"[SynthesisNode] primary_key resolved to: {primary_key!r}")

        primary_docs: List[dict] = list(state.get(primary_key, None) or []) if primary_key else []
        print(f"[SynthesisNode] primary_docs count: {len(primary_docs)}")

        # ── Fallback: collect every non-empty context in priority order ──────────
        # Used when the primary context is empty OR as a supplement.
        _priority_order = [
            "batting_context",
            "bowling_context",
            "venue_context",
            "h2h_context",
            "trend_context",
            "form_context",
        ]

        fallback_docs: List[dict] = []
        if not primary_docs:
            print("[SynthesisNode] primary_docs empty — checking fallback contexts...")
            for key in _priority_order:
                if key == primary_key:
                    continue  # already checked and was empty
                bucket = state.get(key) or []
                if bucket:
                    print(f"[SynthesisNode]   fallback: using {key} (count={len(bucket)})")
                    fallback_docs.extend(bucket)

        docs: List[dict] = primary_docs or fallback_docs
        print(f"[SynthesisNode] final docs to synthesise: {len(docs)}")

        # ── [DEBUG 3] Guard check ─────────────────────────────────────────────
        # ── Guard: nothing retrieved across all contexts ──────────────────────────
        if not docs:
            print("[SynthesisNode] GUARD FIRED — no docs in any context. Returning fallback message.")
            state["final_answer"] = "I could not find the answer in the dataset."
            return state

        # ── Build context string with inline citations ────────────────────────────
        context_parts = []

        for i, d in enumerate(docs, 1):
            meta = d.get("metadata") or {}
            source_meta = []
            for k in ["section", "team", "player", "venue", "season", "source_section"]:
                if meta.get(k) is not None:
                    source_meta.append(f"{k}:{meta.get(k)}")

            citation = f"[source id={d.get('id')} {'; '.join(source_meta)}]"

            context_parts.append(f"Document {i}: {d.get('document')} \n{citation}\n")

        context_text = "\n".join(context_parts)

        # ── [DEBUG 4] Exact prompt context sent to LLM ───────────────────────
        print("[SynthesisNode] === PROMPT CONTEXT SENT TO LLM ===")
        print(context_text)
        print("[SynthesisNode] ===================================")

        question = state.get("user_query", "")

        response = chain.invoke({"question": question, "context": context_text})

        # ── [DEBUG 5] LLM response ────────────────────────────────────────────
        answer = response.content.strip()
        print(f"[SynthesisNode] LLM response: {answer!r}")
        if "could not find" in answer.lower():
            print("[SynthesisNode] NOTE: LLM returned fallback — context was present but "
                  "did not match the question (retrieval mismatch, not a code bug).")

        # Store model output directly; caller can log or further validate
        state["final_answer"] = answer

        return state



if __name__ == "__main__":
    # simple smoke test (requires running chroma and models)
    s = IPLState()
    s["user_query"] = "Who scored the most runs for Mumbai Indians in 2024?"
    s["batting_context"] = []
    n = SynthesisNode()
    print(n.run(s))

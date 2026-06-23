from typing import List

from graph.state import IPLState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

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
    """Synthesizes an answer strictly from the retrieved batting_context and adds final_answer to state."""

    def run(self, state: IPLState) -> IPLState:

        docs: List[dict] = state.get("batting_context") or []

        if not docs:
            state["final_answer"] = "I could not find the answer in the dataset."
            return state

        # Build context string with inline citations using metadata
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

        question = state.get("user_query", "")

        response = chain.invoke({"question": question, "context": context_text})

        # Store model output directly; caller can log or further validate
        state["final_answer"] = response.content.strip()

        return state


if __name__ == "__main__":
    # simple smoke test (requires running chroma and models)
    s = IPLState()
    s["user_query"] = "Who scored the most runs for Mumbai Indians in 2024?"
    s["batting_context"] = []
    n = SynthesisNode()
    print(n.run(s))

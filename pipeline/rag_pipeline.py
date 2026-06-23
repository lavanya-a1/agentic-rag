from utils.query_rewriter import rewrite_query
from retrievers.hybrid_search import hybrid_search

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv()

# ===========================================
# LLM
# ===========================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ===========================================
# Prompt
# ===========================================

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an IPL assistant.

Answer ONLY using the retrieved context.

If the answer is not present in the context,
say:

'I could not find the answer in the dataset.'

Keep the answer concise and factual.
"""
        ),
        (
            "human",
            """
Question:

{question}

Retrieved Context:

{context}

Answer:
"""
        )
    ]
)

chain = prompt | llm


# ===========================================
# Main Pipeline
# ===========================================

def run_pipeline(query):

    # ---------------------------
    # Query Rewrite
    # ---------------------------

    rewritten_query = rewrite_query(query)

    print("\nRewritten Query:")
    print(rewritten_query)

    # ---------------------------
    # Retrieval
    # ---------------------------

    retrieved_docs = hybrid_search(
        rewritten_query,
        top_k=3
    )

    context = ""

    for i, doc in enumerate(retrieved_docs, 1):

        context += f"Document {i}:\n"

        context += doc["document"]

        context += "\n\n"
    # ---------------------------
    # LLM
    # ---------------------------

    response = chain.invoke(

        {
            "question": rewritten_query,
            "context": context
        }

    )

    return response.content
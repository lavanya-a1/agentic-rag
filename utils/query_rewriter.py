from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------
# LLM
# ------------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ------------------------------------
# Prompt
# ------------------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an IPL query rewriting assistant.

Your job is to rewrite the user's question into a
clear and retrieval-friendly query.

Rules:
- Expand abbreviations (MI -> Mumbai Indians, CSK -> Chennai Super Kings).
- Replace pronouns with explicit names whenever possible.
- Keep the meaning exactly the same.
- Do NOT answer the question.
- Return ONLY the rewritten query.
"""
        ),
        ("human", "{query}")
    ]
)

chain = prompt | llm

# ------------------------------------
# Function
# ------------------------------------

def rewrite_query(query: str) -> str:

    response = chain.invoke(
        {"query": query}
    )

    return response.content.strip()


# ------------------------------------
# Test
# ------------------------------------

if __name__ == "__main__":

    while True:

        q = input("\nQuery: ")

        if q.lower() == "exit":
            break

        rewritten = rewrite_query(q)

        print("\nRewritten Query:")
        print(rewritten)

        
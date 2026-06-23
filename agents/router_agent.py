import re


def route_query(query):

    q = query.lower()

    # -------------------------
    # Aggregation Queries
    # -------------------------

    aggregation_words = [

        "highest",
        "lowest",
        "maximum",
        "minimum",
        "most",
        "least",
        "top",
        "best"

    ]

    if any(word in q for word in aggregation_words):

        route = "aggregation"

    # -------------------------
    # Comparison Queries
    # -------------------------

    elif " vs " in q or "compare" in q:

        route = "comparison"

    # -------------------------
    # Reasoning Queries
    # -------------------------

    elif any(word in q for word in [

        "why",
        "explain",
        "reason",
        "better",
        "stronger"

    ]):

        route = "reasoning"

    # -------------------------
    # Default
    # -------------------------

    else:

        route = "retrieval"

    return route


# =====================================

if __name__ == "__main__":

    while True:

        q = input("\nQuery : ")

        if q == "exit":
            break

        print(route_query(q))
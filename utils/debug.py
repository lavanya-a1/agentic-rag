def debug_state(stage, state):
    print(f"\n===== {stage} =====")
    print("QUERY:", state.get("query"))
    print("ROUTE:", state.get("route"))
    
    docs = state.get("docs", [])
    print("DOC COUNT:", len(docs))
    
    print("DOCS:", [
        d.get("metadata", {}).get("venue") if isinstance(d, dict) else str(d)
        for d in docs
    ][:5])
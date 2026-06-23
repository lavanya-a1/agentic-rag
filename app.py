from pipeline.rag_pipeline import run_pipeline

while True:

    query = input("\nAsk IPL Question: ")

    if query.lower() == "exit":
        break

    answer = run_pipeline(query)

    print("\nAnswer:\n")

    print(answer)
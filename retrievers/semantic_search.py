import chromadb
from sentence_transformers import SentenceTransformer

VECTORSTORE_PATH = "vectorstore/chroma_db"
COLLECTION_NAME = "ipl_knowledge_base"

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path=VECTORSTORE_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)

def semantic_search(query, top_k=5):

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    output = []

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    ids = results["ids"][0]
    distances = results["distances"][0]

    for i in range(len(docs)):

        output.append({
            "id": ids[i],
            "document": docs[i],
            "metadata": metas[i],
            "score": distances[i]
        })

    return output


import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# ======================================================
# Configuration
# ======================================================

DATASET_PATH = "json/master_dataset_enriched.json"

VECTORSTORE_PATH = "vectorstore/chroma_db"

COLLECTION_NAME = "ipl_knowledge_base"

# ======================================================
# Load Embedding Model
# ======================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Model loaded.")

# ======================================================
# Load Dataset
# ======================================================

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Loaded {len(dataset)} records.")

# ======================================================
# Create Chroma Client
# ======================================================

client = chromadb.PersistentClient(
    path=VECTORSTORE_PATH
)

# Delete old collection if exists (optional)

try:
    client.delete_collection(COLLECTION_NAME)
except:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME
)

# ======================================================
# Add Records
# ======================================================

for record in dataset:

    text = record["document_text"]

    embedding = model.encode(
        text
    ).tolist()

    metadata = {

        "section": record["section"],

        "entity_type": record["entity_type"],

        "team": record["team"] or "",

        "player": record["player"] or "",

        "venue": record["venue"] or "",

        "season": str(record["season"]),

        "source_section": record["source_section"]

    }

    collection.add(

        ids=[
            str(record["id"])
        ],

        documents=[
            text
        ],

        metadatas=[
            metadata
        ],

        embeddings=[
            embedding
        ]

    )

print()

print("=" * 50)
print("Embeddings successfully created!")
print(f"Collection : {COLLECTION_NAME}")
print(f"Records    : {collection.count()}")
print("=" * 50)
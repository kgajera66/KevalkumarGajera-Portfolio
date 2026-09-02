"""
06_rag_ingest.py
--------------------
Splits the maintenance manuals into chunks, generates an embedding for
each chunk using a LOCAL model (via Ollama), and stores them in a local
vector database (ChromaDB). Run this once whenever the manuals change.

WHY chunk the document instead of embedding the whole thing at once:
embeddings work best on focused, coherent pieces of text -- embedding a
huge multi-topic document as one vector would blur together concepts from
five completely different failure modes into one average, useless for
precise retrieval. Splitting by failure mode (using "---" as a natural
boundary, since we wrote the manual that way) means each chunk stays
focused on ONE topic, so a search for "tool wear" retrieves specifically
the TWF section, not a vague blend of all five.
"""

import chromadb
import ollama

MANUAL_PATH = "manuals/maintenance_manuals.md"

# ============================================================
# STEP 1: Load and chunk the document
# ============================================================

with open(MANUAL_PATH, "r", encoding="utf-8") as f:
    full_text = f.read()

# Split on "---" (the separator we used between failure modes in the
# manual). Each resulting chunk is one complete failure-mode section.
chunks = [chunk.strip() for chunk in full_text.split("---") if chunk.strip()]

print(f"Split manual into {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    title = chunk.split("\n")[0].replace("#", "").strip()
    print(f"  Chunk {i}: {title} ({len(chunk)} characters)")

# ============================================================
# STEP 2: Generate embeddings for each chunk (locally, via Ollama)
# ============================================================

# WHY nomic-embed-text specifically: it's a model purpose-built for
# generating embeddings (turning text into a list of numbers that
# capture meaning), separate from llama3.1 which is built for
# GENERATING text, not embedding it. Using the right specialized model
# for each job is standard practice -- one model to understand/retrieve,
# a different model to reason/respond.
embeddings = []
for chunk in chunks:
    response = ollama.embeddings(model="nomic-embed-text", prompt=chunk)
    embeddings.append(response["embedding"])

print(f"\nGenerated {len(embeddings)} embeddings, "
      f"each with {len(embeddings[0])} dimensions")

# ============================================================
# STEP 3: Store in ChromaDB (a local, on-disk vector database)
# ============================================================

# PersistentClient saves to disk in ./chroma_db -- so you don't need to
# re-embed everything every time you restart Python, only when the
# source manual actually changes.
client = chromadb.PersistentClient(path="./chroma_db")

# get_or_create_collection avoids an error if you re-run this script --
# it reuses the existing collection instead of failing on a duplicate.
collection = client.get_or_create_collection(name="maintenance_manuals")

collection.upsert(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    embeddings=embeddings,
    documents=chunks,
)

print(f"\nStored {len(chunks)} chunks in ChromaDB collection 'maintenance_manuals'")
print("Ready for querying -- run 07_rag_query.py next.")

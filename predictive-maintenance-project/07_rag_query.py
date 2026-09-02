"""
07_rag_query.py
--------------------
Takes a technician's question, retrieves the most relevant manual
chunk(s) from ChromaDB, and asks the LOCAL LLM (llama3.1 via Ollama) to
answer using ONLY that retrieved content -- not its own general
knowledge. This is the core RAG pattern: retrieval BEFORE generation,
so the answer is grounded in your actual documents.
"""

import chromadb
import ollama

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="maintenance_manuals")


def answer_question(question: str, n_results: int = 2) -> str:
    # ============================================================
    # STEP 1: Embed the question with the SAME embedding model used
    # for the manuals.
    # ============================================================
    question_embedding = ollama.embeddings(
        model="nomic-embed-text", prompt=question
    )["embedding"]

    # ============================================================
    # STEP 2: Retrieve the most similar chunk(s) from the vector database.
    # n_results=2 retrieves the top 2 closest matches, not just 1 --
    # this gives the LLM a little more context in case the question
    # spans two failure modes, at the cost of a slightly longer prompt.
    # ============================================================
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results,
    )

    retrieved_chunks = results["documents"][0]
    context = "\n\n---\n\n".join(retrieved_chunks)

    # ============================================================
    # STEP 3: Generate an answer using ONLY the retrieved context.
    # This is the critical RAG instruction: "answer using ONLY the
    # provided context" stops the model from blending in its own
    # general training knowledge, which might be subtly wrong for
    # specific equipment and thresholds.
    # ============================================================
    prompt = f"""You are a maintenance assistant. Answer the technician's
question using ONLY the manual excerpts below. If the excerpts don't
contain enough information to answer, say so clearly rather than
guessing or using outside knowledge.

Manual excerpts:
{context}

Technician's question: {question}

Answer:"""

    response = ollama.generate(model="llama3.1:8b", prompt=prompt)
    return response["response"], retrieved_chunks


if __name__ == "__main__":
    test_questions = [
        "The tool wear counter shows 210 minutes and torque looks high. What should I do?",
        "A machine is running cool but slow, and the temperature difference is small. What's wrong?",
        "How do I prevent overstrain failures on low quality variant machines?",
    ]

    for question in test_questions:
        print(f"\n{'=' * 70}")
        print(f"Q: {question}")
        print(f"{'=' * 70}")
        answer, sources = answer_question(question)
        print(f"\nA: {answer}")
        print(f"\n[Retrieved from {len(sources)} chunk(s)]")

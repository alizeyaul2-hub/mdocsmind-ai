import os

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found in the .env file")


# --------------------------------------------------
# 2. Create the SAME embedding model
# --------------------------------------------------

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# --------------------------------------------------
# 3. Load existing ChromaDB
# --------------------------------------------------

vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)


# --------------------------------------------------
# 4. Create retriever
# --------------------------------------------------

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 10
    }
)


# --------------------------------------------------
# 5. Ask a question
# --------------------------------------------------

question = input("Ask a question about the PDF: ")


# --------------------------------------------------
# 6. Retrieve relevant chunks
# --------------------------------------------------

retrieved_docs = retriever.invoke(question)


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("\nRetrieved chunks:")
print("=" * 60)

for i, doc in enumerate(retrieved_docs, start=1):

    print(f"\n--- Chunk {i} ---")

    print(doc.page_content)

    print("\nMetadata:")
    print(doc.metadata)

    print("=" * 60)
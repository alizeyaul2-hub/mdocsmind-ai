import os

from dotenv import load_dotenv
from pydantic import SecretStr

# pyrefly: ignore [missing-import]
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_chroma import Chroma


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found in the .env file")

api_key = SecretStr(api_key)


# --------------------------------------------------
# 2. Create the SAME embedding model
#    used when creating ChromaDB
# --------------------------------------------------

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    api_key=api_key
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
# 5. Create Gemini chat model
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=api_key
)


# --------------------------------------------------
# 6. Ask the user for a question
# --------------------------------------------------

question = input("\nAsk a question: ")


# --------------------------------------------------
# 7. Retrieve relevant chunks
# --------------------------------------------------

retrieved_docs = retriever.invoke(question)


# --------------------------------------------------
# 8. Combine retrieved chunks
# --------------------------------------------------

context = "\n\n".join(
    doc.page_content
    for doc in retrieved_docs
)


# --------------------------------------------------
# 9. Create prompt
# --------------------------------------------------

prompt = f"""
You are a helpful PDF assistant.

Answer the user's question using ONLY the information
provided in the context.

If the answer is not available in the context, say:

"I could not find the answer in the PDF."

Do not make up information.

Context:
{context}

User Question:
{question}
"""


# --------------------------------------------------
# 10. Send prompt to Gemini
# --------------------------------------------------

response = llm.invoke(prompt)

print("\nAnswer:")

if isinstance(response.content, list):
    for item in response.content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text", ""))
else:
    print(response.content)
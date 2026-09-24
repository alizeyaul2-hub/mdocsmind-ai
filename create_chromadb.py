import os

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found in the .env file")


# --------------------------------------------------
# 2. Load PDF
# --------------------------------------------------

pdf_path = "./pdfs/GRU.pdf"

loader = PyPDFLoader(pdf_path)

documents = loader.load()

print("PDF loaded successfully!")
print("Number of pages:", len(documents))


# --------------------------------------------------
# 3. Split PDF into chunks
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print("Number of chunks:", len(chunks))


# --------------------------------------------------
# 4. Create Gemini embedding model
# --------------------------------------------------

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# --------------------------------------------------
# 5. Create ChromaDB
# --------------------------------------------------

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)


# --------------------------------------------------
# 6. Display result
# --------------------------------------------------

print("\nChromaDB created successfully!")

print("Database location:")
print("./chroma_db")
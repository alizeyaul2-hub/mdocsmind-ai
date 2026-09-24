import os

from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


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


# --------------------------------------------------
# 3. Split PDF into chunks
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)


# --------------------------------------------------
# 4. Create Gemini embedding model
# --------------------------------------------------

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# --------------------------------------------------
# 5. Test embedding
# --------------------------------------------------

test_text = chunks[0].page_content

embedding = embedding_model.embed_query(test_text)


# --------------------------------------------------
# 6. Display result
# --------------------------------------------------

print("Embedding model loaded successfully!")

print("\nNumber of chunks:", len(chunks))

print("Embedding vector length:", len(embedding))

print("\nFirst 10 embedding values:")
print(embedding[:10])
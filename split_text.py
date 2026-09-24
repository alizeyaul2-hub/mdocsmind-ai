from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# 1. Load PDF
# --------------------------------------------------

pdf_path = "./pdfs/GRU.pdf"

loader = PyPDFLoader(pdf_path)

documents = loader.load()


# --------------------------------------------------
# 2. Create text splitter
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


# --------------------------------------------------
# 3. Split documents into chunks
# --------------------------------------------------

chunks = text_splitter.split_documents(documents)


# --------------------------------------------------
# 4. Display information
# --------------------------------------------------

print("PDF loaded successfully!")
print("Number of pages:", len(documents))

print("\nText splitting completed!")
print("Number of chunks:", len(chunks))


# --------------------------------------------------
# 5. Display first chunk
# --------------------------------------------------

print("\nFirst chunk:")
print(chunks[0].page_content)
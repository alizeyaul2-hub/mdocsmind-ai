from langchain_community.document_loaders import PyPDFLoader


# PDF file path
pdf_path = "./pdfs/GRU.pdf"


# Create PDF loader
loader = PyPDFLoader(pdf_path)


# Load PDF
documents = loader.load()


# Display information
print("PDF loaded successfully!")
print("Number of pages:", len(documents))

print("\nFirst page content:")
print(documents[0].page_content)
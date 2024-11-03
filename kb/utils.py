
from langchain_community.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader
import warnings

# ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

def load_document(file_path: str):
    # Loads the document from the local directory

    if file_path.endswith(".pdf"):
        # Load PDF files using PyPDFLoader
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif file_path.endswith(".docx"):
        # Load DOCX files using Docx2txtLoader
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    elif file_path.endswith(".csv"):
        # Load CSV files with CSVLoader
        loader = CSVLoader(file_path)
        docs = loader.load()
    else:
        # if unidentified file type, use unstructured loader
        loader = TextLoader(file_path)
        docs = loader.load()

    return docs[0]


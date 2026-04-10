from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
# from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

# Paso 1: Cargar todos los archivos .md con documentos de la carpeta docs.
loader = DirectoryLoader("docs/", glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
documents = loader.load()

# Paso 2: Partir en chunks
# ¿Por qué? Porque el documento entero puede ser muy largo.
# El LLM necesita pedazos pequeños y relevantes, no todo el texto.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = text_splitter.split_documents(documents)

# Paso 3: Verificar si la collection ya existe en Qdrant
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collections = qdrant_client.get_collections().collections
collection_names = [c.name for c in collections]

embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

if "onboarding_docs" not in collection_names:
    # Primera vez: crea la collection y sube los chunks
    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        collection_name="onboarding_docs"
    )
else:
    # Ya existe: solo se conecta, no duplica datos
    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        collection_name="onboarding_docs"
    )
# # Paso 3: Crear embeddings y guardar en ChromaDB
# # Embedding = convertir texto a un vector numérico para búsqueda semántica
# embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
# # vectorstore = Chroma.from_documents( migramos de vector DB desde chromadb a qdrant cloud )
# vectorstore = QdrantVectorStore.from_documents(
#     documents=chunks,
#     embedding=embeddings,
#     # persist_directory="./chroma_db" #se guarda en disco 
#     url=os.getenv("QDRANT_URL"),
#     api_key=os.getenv("QDRANT_API_KEY"),
#     collection_name="onboarding_docs"
# )

# Paso 4: Función para buscar contexto relevante
def search_context(query: str, k: int= 5) -> str:
    """
    Recibe una pregunta, busca los chunks más relevantes
    y devuelve el contexto como texto.
    k = cantidad de chunks a retornar
    """
    results = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in results])
    return context 
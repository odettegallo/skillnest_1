import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY en el archivo ".env".')

# Inicializamos la misma función de embeddings (no hará llamadas a la API al solo contar)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Reconexión al índice persistido en disco
vectorstore_recargado = Chroma(
    persist_directory="vectorstore/",
    embedding_function=embeddings,
)

total_documentos = vectorstore_recargado._collection.count()
print(f"Documentos recuperados desde disco: {total_documentos}")
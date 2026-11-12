import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# 0. Cargar variables de entorno y verificar API Key
load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY en el archivo ".env".')

# 1. Corpus propio (al menos 5 documentos relacionados con la arquitectura de tu app)
corpus = [
    "El cliente HTTP implementa reintentos exponenciales hasta 3 veces ante un TimeoutError.",
    "Los errores de autenticación (401/403) nunca se reintentan: fallan de inmediato con un ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
    "El agente supervisor decide qué herramienta o cadena ejecutar según la descripción semántica de cada ruta.",
    "Las pruebas unitarias del repositorio usan mocks para validar las trazas sin consumir cuota real de la API.",
    "El pipeline de limpieza normaliza espacios y saltos de línea antes de enviar el texto al modelo de embeddings.",
]

# 2. Chunking (convertimos los strings en objetos Document)
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
chunks = splitter.create_documents(corpus)

# 3. Embeddings reales
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 4. Construcción y persistencia en disco en 'vectorstore/'
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="vectorstore/",
)

print(f"Indexados {len(chunks)} chunks en vectorstore/")
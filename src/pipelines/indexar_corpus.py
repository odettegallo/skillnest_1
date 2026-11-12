import os
import time
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# 1. Definir la ruta absoluta y el nombre de la colección por defecto
PERSIST_DIR = os.path.abspath("vectorstore")
COLLECTION_NAME = "corpus_ejemplo"


def con_reintentos(operacion, max_intentos=4, espera_inicial=5):
    """Función de utilidad para reintentar operaciones a la API ante el error 429."""
    espera = espera_inicial
    for intento in range(1, max_intentos + 1):
        try:
            return operacion()
        except Exception as error:
            mensaje = str(error)
            es_limite = "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje
            if not es_limite or intento == max_intentos:
                raise
            print(f"Límite de peticiones alcanzado. Reintento {intento} de {max_intentos - 1} en {espera} s...")
            time.sleep(espera)
            espera *= 2


def indexar_corpus(corpus, persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME, chunk_size=200, chunk_overlap=30):
    """Parte, calcula embeddings con reintentos y persiste un corpus en Chroma."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY en el archivo ".env".')

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.create_documents(corpus)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # Invocamos Chroma dentro del manejador de reintentos ante saturación de cuota
    vectorstore = con_reintentos(
        lambda: Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=persist_dir,
        )
    )
    
    print(f"Ruta del índice: {persist_dir}")
    print(f"Colección: {collection_name}")
    print(f"Chunks indexados: {len(chunks)}")
    return vectorstore


def cargar_vectorstore(persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME):
    """Reconecta a un vector store ya indexado usando ruta absoluta y colección explícita."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY en el archivo ".env".')

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
    
    print(f"Ruta del índice: {persist_dir}")
    print(f"Colección: {vectorstore._collection.name}")
    print(f"Chunks en disco: {vectorstore._collection.count()}")
    return vectorstore


if __name__ == "__main__":
    corpus_prueba = [
        "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
        "El costo de cada llamada se calcula a partir de totalTokenCount.",
        "Las pruebas unitarias del cliente usan mocks y corren en menos de un segundo.",
    ]

    # Indexamos con la nueva estructura robusta
    indexar_corpus(corpus_prueba)

    print("\n--- Verificando recarga ---")
    # Probamos reconectarnos
    vectorstore_recargado = cargar_vectorstore()
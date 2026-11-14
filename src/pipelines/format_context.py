import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from core.config import MODELOS_DISPONIBLES

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY en el archivo ".env".')

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def formatear_contexto(chunks_recuperados):
    """Arma un bloque de contexto numerado para el prompt, y un mapa
    numero -> fuente para reconstruir la cita despues."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas


def construir_prompt(pregunta, persist_directory="vectorstore/", k=3):
    """Recupera los k chunks mas relevantes para la pregunta y arma
    el prompt dinamico con contexto numerado, listo para pasarle al modelo."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    chunks_recuperados = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks_recuperados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return prompt, citas


def invocar_con_fallback(prompt):
    """Invoca a Gemini rotando por los modelos disponibles en MODELOS_DISPONIBLES si hay errores 429."""
    for idx, modelo_nombre in enumerate(MODELOS_DISPONIBLES):
        try:
            print(f"🔄 Probando con modelo [{idx + 1}/{len(MODELOS_DISPONIBLES)}]: {modelo_nombre}")
            llm = ChatGoogleGenerativeAI(model=modelo_nombre, temperature=0)
            respuesta = llm.invoke(prompt)
            return respuesta.content, modelo_nombre
        except Exception as error:
            mensaje = str(error)
            if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
                print(f"⚠️ Límite alcanzado con {modelo_nombre}. Rotando...")
                continue
            else:
                raise error
    raise RuntimeError("❌ Se agotaron todos los modelos disponibles por límite de cuota.")


if __name__ == "__main__":
    # --- PASO OPCIONAL DE REINDEXACIÓN ---
    reindexar = False  # Cambia a True si necesitas reindexar desde cero con metadatas
    
    if reindexar:
        corpus = [
            "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
            "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
            "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
            "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
            "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
        ]
        metadatas = [{"fuente": f"doc{i}.md"} for i in range(len(corpus))]
        ids = [f"doc{i}" for i in range(len(corpus))]

        splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
        chunks = splitter.create_documents(corpus, metadatas=metadatas)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            ids=ids,
            persist_directory="vectorstore/"
        )
        print("Vectorstore reindexado correctamente con metadatas e IDs.")

    print("\n" + "="*50)
    print("EJECUTANDO ESCENARIOS DE PRUEBA DE LA ACTIVIDAD")
    print("="*50)

    # --- ESCENARIO 1: Dos preguntas distintas (verificar recuperación semántica) ---
    print("\n[Escenario 1] Probando dos preguntas distintas:")
    p1 = "Que hace el cliente si hay un TimeoutError?"
    p2 = "Cuanto cuesta cada llamada?"
    
    prompt1, citas1 = construir_prompt(pregunta=p1, persist_directory="vectorstore/", k=2)
    prompt2, citas2 = construir_prompt(pregunta=p2, persist_directory="vectorstore/", k=2)
    
    print(f"Pregunta 1: '{p1}' -> Citas obtenidas: {list(citas1.values())}")
    print(f"Pregunta 2: '{p2}' -> Citas obtenidas: {list(citas2.values())}")

    # --- ESCENARIO 2: Pregunta fuera del corpus (evaluar respuesta negativa) ---
    print("\n[Escenario 2] Pregunta que el corpus NO puede responder:")
    pregunta_fuera = "Cual es la capital de Francia?"
    prompt_fuera, _ = construir_prompt(pregunta=pregunta_fuera, persist_directory="vectorstore/", k=2)
    
    respuesta_texto, modelo_usado = invocar_con_fallback(prompt_fuera)
    print(f"Pregunta: '{pregunta_fuera}'")
    print(f"Respuesta del modelo ({modelo_usado}):\n{respuesta_texto}")

    # --- ESCENARIO 3: Verificación manual de una cita ---
    print("\n[Escenario 3] Verificación manual de citas:")
    # Hacemos una pregunta real y evaluamos la respuesta con el LLM
    prompt_real, citas_real = construir_prompt(pregunta=p1, persist_directory="vectorstore/", k=2)
    respuesta_real, _ = invocar_con_fallback(prompt_real)
    print(f"Pregunta: '{p1}'")
    print(f"Respuesta generada:\n{respuesta_real}")
    print(f"Mapa de citas completo: {citas_real}")
    print(f"Verificación: La cita [1] apunta al archivo -> {citas_real.get(1)}")
import os
import faiss
import openai
import numpy as np
import pickle

# Configuración de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
embedding_model = "text-embedding-3-small"

# 🔍 Función para consultar los fragmentos más relevantes desde el índice FAISS
def buscar_en_base(pregunta: str, k: int = 3) -> str:
    # Cargar índice y metadatos
    index = faiss.read_index("indice_faiss.index")
    with open("metadata.pkl", "rb") as f:
        textos, metadatos = pickle.load(f)

    # Generar embedding de la pregunta
    response = openai.embeddings.create(
        input=[pregunta],
        model=embedding_model
    )
    vector = np.array(response.data[0].embedding).astype("float32").reshape(1, -1)

    # Buscar los k fragmentos más similares
    _, indices = index.search(vector, k)

    # Construir el contexto para la respuesta
    contexto = "\n\n".join([textos[i] for i in indices[0]])
    return contexto

import os
import fitz  # PyMuPDF
import openai
import faiss
import numpy as np
import pickle
from typing import List

# Configuración
openai.api_key = os.getenv("OPENAI_API_KEY")
embedding_model = "text-embedding-3-small"
pdf_dir = "./pdfs"  # Ruta local a tus PDFs
index_file = "indice_faiss.index"
metadata_file = "metadata.pkl"

# Extraer texto de cada PDF
def extraer_texto_pdf(path: str) -> str:
    doc = fitz.open(path)
    return " ".join([page.get_text() for page in doc])

# Dividir texto en fragmentos
def dividir_en_chunks(texto: str, max_tokens: int = 500) -> List[str]:
    oraciones = texto.split(". ")
    chunks, actual = [], ""
    for oracion in oraciones:
        if len(actual) + len(oracion) < max_tokens * 5:
            actual += oracion + ". "
        else:
            chunks.append(actual.strip())
            actual = oracion + ". "
    if actual:
        chunks.append(actual.strip())
    return chunks

# Obtener embedding de texto
def obtener_embedding(texto: str) -> List[float]:
    response = openai.embeddings.create(input=[texto], model=embedding_model)
    return response.data[0].embedding

# Crear índice FAISS desde PDFs
def crear_indice():
    textos = []
    metadatos = []
    archivos = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    for archivo in archivos:
        texto = extraer_texto_pdf(os.path.join(pdf_dir, archivo))
        chunks = dividir_en_chunks(texto)
        for chunk in chunks:
            textos.append(chunk)
            metadatos.append({"documento": archivo})

    vectores = np.array([obtener_embedding(t) for t in textos]).astype("float32")
    index = faiss.IndexFlatL2(len(vectores[0]))
    index.add(vectores)

    with open(metadata_file, "wb") as f:
        pickle.dump((textos, metadatos), f)
    faiss.write_index(index, index_file)

    print(f"✅ Índice creado con {len(textos)} fragmentos.")

if __name__ == "__main__":
    crear_indice()

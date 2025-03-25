import os
import time
from notion_client import Client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

# Carregar variáveis de ambiente
load_dotenv()

# Configurar API do Notion
notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Carregar o modelo de embeddings do Sentence Transformers
model = SentenceTransformer('all-MiniLM-L6-v2')

# Definir um limiar mínimo de similaridade
SIMILARITY_THRESHOLD = 0.5

# Cache para evitar chamadas desnecessárias ao Notion
@lru_cache(maxsize=1)
def get_notion_data():
    """Busca as perguntas e respostas do Notion e calcula os embeddings antecipadamente."""
    try:
        results = notion.databases.query(database_id=DATABASE_ID)
    except Exception as e:
        print(f"Erro ao conectar com o Notion: {e}")
        return []

    documents = []
    for page in results.get("results", []):
        properties = page["properties"]
        question = properties.get("Pergunta", {}).get("title", [{}])[0].get("text", {}).get("content", "Sem pergunta")
        rich_text_list = properties.get("Resposta", {}).get("rich_text", [])
        answer = " ".join([block.get("text", {}).get("content", "") for block in rich_text_list])
        question_embedding = model.encode(question)  # Pré-calcular embedding
        documents.append({"question": question, "answer": answer, "embedding": question_embedding})
    
    return documents

# Função para buscar a melhor resposta
def ask_oracle(query, notion_data):
    """Consulta a IA e retorna a melhor resposta, usando o Notion como base."""
    notion_data = get_notion_data()
    if not notion_data:
        return "Nenhuma informação disponível no momento."

    query_embedding = model.encode(query)
    best_match = None
    max_similarity = -1
    
    for data in notion_data:
        similarity = cosine_similarity([query_embedding], [data['embedding']])[0][0]

        if similarity > max_similarity:
            max_similarity = similarity
            best_match = data

    if max_similarity > SIMILARITY_THRESHOLD:
        return best_match['answer']
    else:
        return "Não encontrei uma resposta relevante. Tente reformular sua pergunta."

if __name__ == "__main__":
    notion_data = get_notion_data()

    if notion_data:
        print("Perguntas e respostas do Notion carregadas.")

        while True:
            query = input("Digite sua pergunta: ")
            if query.lower() == "sair":
                break

            resposta = ask_oracle(query)
            print("\nOráculo:", resposta, "\n")
    else:
        print("Nenhum dado encontrado no Notion.")

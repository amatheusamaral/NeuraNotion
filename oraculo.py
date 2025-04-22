import os
from notion_client import Client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Carregar variáveis de ambiente
load_dotenv()

# Configurar API do Notion
notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Limiar de similaridade para considerar como uma resposta relevante
SIMILARITY_THRESHOLD = 0.5

# Carregar o modelo de embeddings do Sentence Transformers
try:
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./model_cache')
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    model = None

def get_notion_data():
    """Busca as perguntas e respostas do Notion e calcula os embeddings antecipadamente."""
    if not model:
        return []

    try:
        results = notion.databases.query(database_id=DATABASE_ID)
    except Exception as e:
        print(f"Erro ao conectar com o Notion: {e}")
        return []

    documents = []
    for page in results.get("results", []):
        try:
            properties = page["properties"]
            question = properties["Pergunta"]["title"][0]["text"]["content"]
            answer = properties["Resposta"]["rich_text"][0]["text"]["content"]
            question_embedding = model.encode(question)
            documents.append({"question": question, "answer": answer, "embedding": question_embedding})
        except Exception as e:
            print(f"Erro ao processar página do Notion: {e}")
            continue

    return documents

def ask_oracle(query, notion_data):
    """Consulta a IA e retorna a melhor resposta, usando o Notion como base."""
    if not model or not notion_data:
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
    if not notion_data:
        print("Não foi possível carregar dados do Notion.")
    else:
        print("Perguntas e respostas do Notion carregadas.")

    while True:
        query = input("Digite sua pergunta ('sair' para encerrar): ")
        if query.lower() == "sair":
            break
        resposta = ask_oracle(query, notion_data)
        print("\nOráculo:", resposta, "\n")

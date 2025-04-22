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

# Carregar o modelo de embeddings do Sentence Transformers
model = SentenceTransformer('paraphrase-MiniLM-L6-v2') 

# Limiar de similaridade para considerar como uma resposta relevante
SIMILARITY_THRESHOLD = 0.5

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
        question = properties["Pergunta"]["title"][0]["text"]["content"] if "Pergunta" in properties else "Sem pergunta"
        answer = properties["Resposta"]["rich_text"][0]["text"]["content"] if "Resposta" in properties else "Sem resposta"
        
        question_embedding = model.encode(question)  # Pré-calcular embedding para a pergunta
        documents.append({"question": question, "answer": answer, "embedding": question_embedding})
    
    return documents

def ask_oracle(query, notion_data):
    """Consulta a IA e retorna a melhor resposta, usando o Notion como base."""
    if not notion_data:
        return "Nenhuma informação disponível no momento."

    query_embedding = model.encode(query)
    best_match = None
    max_similarity = -1
    
    # Comparar a consulta com todas as perguntas armazenadas no Notion
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
    while True:
        query = input("Digite sua pergunta: ")

        if query.lower() == "sair":
            break

        notion_data = get_notion_data()  # Carregar dados do Notion sempre que uma nova pergunta for feita

        if notion_data:
            print("Perguntas e respostas do Notion carregadas.")
            resposta = ask_oracle(query, notion_data)
            print("\nOráculo:", resposta, "\n")
        else:
            print("Nenhum dado encontrado no Notion.")

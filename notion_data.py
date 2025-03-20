import os
from notion_client import Client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Carregar variáveis de ambiente
load_dotenv()

# Configurar API do Notion
notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Carregar o modelo de embeddings do Sentence Transformers
model = SentenceTransformer('paraphrase-MiniLM-L6-v2') 

def get_notion_data():
    """Busca as perguntas e respostas do Notion."""
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
        documents.append(f"Pergunta: {question}\nResposta: {answer}")
    
    return documents

def generate_embeddings_from_notion_data(notion_data, max_length=512):
    """Gera embeddings a partir das perguntas e respostas do Notion, com limite de comprimento."""
    truncated_data = []
    for text in notion_data:
        # Truncar o texto de forma mais robusta
        if len(text) > max_length:
            text = text[:max_length]  # Truncar o texto para o comprimento máximo
        truncated_data.append(text)
    
    # Gerar embeddings para os textos truncados
    embeddings = model.encode(truncated_data)
    return embeddings

if __name__ == "__main__":
    notion_data = get_notion_data()
    
    if notion_data:
        print("Perguntas e respostas do Notion:")
        for d in notion_data:
            print(d)
        
        # Gerar embeddings baseados nos dados do Notion com um limite de tamanho (max_length)
        embeddings = generate_embeddings_from_notion_data(notion_data, max_length=512) 
        print("\nEmbeddings gerados:")
        print(embeddings)
    else:
        print("Nenhum dado encontrado no Notion.")

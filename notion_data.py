import os
from notion_client import Client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import streamlit as st

# Carregar variáveis de ambiente
load_dotenv()

# Configurar API do Notion
notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Carregar o modelo de embeddings do Sentence Transformers
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def parse_rich_text(rich_text_array):
    """Transforma o array de rich_text do Notion em texto formatado (Markdown)."""
    result = ""
    for item in rich_text_array:
        text = item.get("text", {})
        content = text.get("content", "")
        link = text.get("link", {}).get("url")
        if link:
            result += f"[{content}]({link})"  # Formatação Markdown para links
        else:
            result += content
    return result

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
        answer = parse_rich_text(properties["Resposta"]["rich_text"]) if "Resposta" in properties else "Sem resposta"
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

# Função para mostrar a resposta no Streamlit
def show_response(resposta):
    """Exibe a resposta de maneira clara, com links corretamente formatados no Streamlit."""
    # Renderizando o texto de forma simples, sem HTML diretamente
    st.subheader("Resposta:")
    st.text(resposta)  # Apenas texto, sem formatação HTML

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
    
    # Exibir a resposta no Streamlit
    st.title("🤖 Assistente FABAPAR")
    st.markdown("Tem uma dúvida? O assistente está aqui para esclarecer! ✨")
    
    query = st.text_input("Digite sua pergunta...", key="query", placeholder="Digite sua pergunta...", label_visibility="hidden")
    
    if query:
        # Exemplo de resposta com link
        resposta = "Aqui está a resposta com um link: [Clique aqui para acessar](https://example.com) e mais texto aqui."
        show_response(resposta)

import streamlit as st
import time
import firebase_admin
from firebase_admin import credentials, firestore
from oraculo import ask_oracle, get_notion_data  # Importando a função get_notion_data
from datetime import datetime

# Inicializando o Firebase Admin SDK (evitando duplicação)
cred = credentials.Certificate('./chaves/neuranotion-fabapar-firebase-adminsdk-fbsvc-86f22a543a.json')


# Verifica se o app já foi inicializado, se não, inicializa
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
else:
    firebase_admin.get_app()  # Caso o app já exista, usa o app existente

# Função para salvar a pergunta no Firestore
def salvar_pergunta(pergunta):
    db = firestore.client()
    perguntas_ref = db.collection("perguntas")
    perguntas_ref.add({
        'pergunta': pergunta,
        'timestamp': firestore.SERVER_TIMESTAMP  # Usar o timestamp do Firestore
    })

# Função para carregar o histórico de perguntas do Firestore
def carregar_historico():
    db = firestore.client()
    perguntas_ref = db.collection("perguntas").order_by('timestamp', direction=firestore.Query.DESCENDING)  # Ordena pelo timestamp
    perguntas = perguntas_ref.stream()
    historico = []
    for pergunta in perguntas:
        historico.append(pergunta.to_dict())
    return historico

# Exibe sugestões baseadas no histórico
def exibir_sugestoes():
    historico = carregar_historico()
    perguntas_passadas = [h['pergunta'] for h in historico]
    if perguntas_passadas:
        st.sidebar.write("Perguntas frequentes:")
        for pergunta in perguntas_passadas[:5]:  # Exibe as últimas 5 perguntas
            st.sidebar.write(f"- {pergunta}")

# Carregar dados do Notion
notion_data = get_notion_data()

st.title(" 🤖 Assistente FABAPAR")
st.write("🧠 Tem uma dúvida? O assistente está aqui para esclarecer! Faça sua pergunta! ✨")

# Exibir sugestões antes da pergunta
exibir_sugestoes()

query = st.text_input("Digite sua pergunta:")

def typing_effect(text, delay=0.03):
    """Função para simular o efeito de digitação."""
    output = st.empty()  # Criar um marcador vazio onde o texto será mostrado
    for i in range(len(text)+1):
        output.markdown(f"<p style='font-size: 16px; font-family: Arial, sans-serif;'>{text[:i]}</p>", unsafe_allow_html=True)  
        time.sleep(delay)

if st.button("Perguntar"):
    if query:
        # Passando tanto a query quanto os dados do Notion para a função ask_oracle
        resposta = ask_oracle(query, notion_data)
        st.write("### Resposta:")
        typing_effect(resposta)

        # Salvar a pergunta no Firebase
        salvar_pergunta(query)

        # Feedback do usuário
        feedback = st.radio("Avalie a resposta:", ("Útil", "Não útil"))

        if feedback:
            # Salvar o feedback no Firestore
            db = firestore.client()
            feedback_ref = db.collection("feedbacks")
            feedback_ref.add({
                'pergunta': query,
                'resposta': resposta,
                'feedback': feedback,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            st.write(f"Obrigado pelo seu feedback: {feedback}!")

st.markdown(""" 
    --- 
    <p style="text-align: center; color: gray; font-size: 14px;">© 2025 Matheus Amaral. Todos os direitos reservados.</p>
""", unsafe_allow_html=True)

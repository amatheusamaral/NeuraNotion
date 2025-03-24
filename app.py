import streamlit as st
import time
import json
from oraculo import ask_oracle, get_notion_data  # Importando a função get_notion_data
from datetime import datetime
from supabase import create_client
from collections import Counter

SUPABASE_URL = "https://dlnkrqvdmqlvbywycvcl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsbmtycXZkbXFsdmJ5d3ljdmNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4MjE5MTIsImV4cCI6MjA1ODM5NzkxMn0.fUY104cBJrV-Jk9P9Zix--zlNb9rLCzKrANU6xmSueQ"

# Criando cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para salvar pergunta no Supabase
def salvar_pergunta(pergunta, resposta):
    data = {
        "pergunta": pergunta,
        "resposta": resposta,
        "timestamp": datetime.now().isoformat()  # Convertendo para string serializável
    }
    response = supabase.table("perguntas").insert(data).execute()
    return response.data[0]["id"]

# Função para salvar feedback no Supabase
def salvar_feedback(pergunta_id, feedback, comentario=""):
    data = {
        "pergunta_id": pergunta_id,
        "feedback": feedback,
        "comentario": comentario,
        "timestamp": datetime.now().isoformat()  # Convertendo para string serializável
    }
    supabase.table("feedbacks").insert(data).execute()

# Função para buscar as perguntas mais feitas
def buscar_perguntas_mais_frequentes():
    response = supabase.table("perguntas").select("pergunta").execute()
    perguntas = response.data
    
    # Contando a frequência das perguntas
    perguntas_contadas = Counter([p['pergunta'].strip().lower() for p in perguntas])  # Ignorando variações de maiúsculas/minúsculas e espaços
    
    # Pegando as 5 perguntas mais frequentes
    perguntas_frequentes = perguntas_contadas.most_common(5)
    
    # Retornando as perguntas no formato original, sem variações de formato
    perguntas_frequentes_formatadas = [
        (pergunta, count) for pergunta, count in perguntas_frequentes
    ]
    
    return perguntas_frequentes_formatadas

# Carregar dados do Notion
notion_data = get_notion_data()

# Layout com o menu lateral
st.sidebar.title("Perguntas mais frequentes")
perguntas_frequentes = buscar_perguntas_mais_frequentes()

# Exibindo as perguntas no menu lateral
for pergunta, _ in perguntas_frequentes:
    # Garantir que as perguntas são exibidas com o formato padronizado (ex: "Como solicitar férias?")
    st.sidebar.write(f"- {pergunta.capitalize()}")  # Capitaliza a primeira letra da pergunta

# Interface principal
st.title(" 🤖 Assistente FABAPAR")
st.write("🧠 Tem uma dúvida? O assistente está aqui para esclarecer! Faça sua pergunta! ✨")

query = st.text_input("Digite sua pergunta:")

def typing_effect(text, delay=0.03):
    output = st.empty()
    for i in range(len(text)+1):
        output.markdown(f"{text[:i]}", unsafe_allow_html=True)
        time.sleep(delay)

if st.button("Perguntar"):
    if query:
        resposta = ask_oracle(query, notion_data)
        st.write("### Resposta:")
        typing_effect(resposta)

        # Salvar pergunta e resposta no Supabase
        pergunta_id = salvar_pergunta(query, resposta)

        # Feedback do usuário
        feedback = st.radio("Avalie a resposta:", ("Útil", "Não útil"))

        if feedback:
            comentario = ""
            if feedback == "Não útil":
                comentario = st.text_area("Como podemos melhorar?")
                if st.button("Enviar Comentário"):
                    salvar_feedback(pergunta_id, False, comentario)
                    st.success("Obrigado pelo feedback!")
            else:
                salvar_feedback(pergunta_id, True)
                st.success("Obrigado pelo feedback!")

st.markdown(""" 
    --- 
    <p style="text-align: center; color: gray; font-size: 14px;">© 2025 Matheus Amaral. Todos os direitos reservados.</p>
""", unsafe_allow_html=True)

import streamlit as st
import time
from oraculo import ask_oracle, get_notion_data
from datetime import datetime
from supabase import create_client
from collections import Counter

# Defina o estilo CSS para os botões
st.markdown("""
    <style>
        .small-button {
            background-color: #f0f0f0;
            color: #333;
            border: 1px solid #ccc;
            padding: 5px 15px;
            font-size: 12px;
            border-radius: 15px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .small-button:hover {
            background-color: #e0e0e0;
        }

        .small-button:active {
            background-color: #d0d0d0;
        }
    </style>
""", unsafe_allow_html=True)

# Funções e variáveis do seu código
SUPABASE_URL = "https://dlnkrqvdmqlvbywycvcl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsbmtycXZkbXFsdmJ5d3ljdmNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4MjE5MTIsImV4cCI6MjA1ODM5NzkxMn0.fUY104cBJrV-Jk9P9Zix--zlNb9rLCzKrANU6xmSueQ"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def salvar_pergunta(pergunta, resposta):
    data = {
        "pergunta": pergunta,
        "resposta": resposta,
        "timestamp": datetime.now().isoformat()
    }
    response = supabase.table("perguntas").insert(data).execute()
    return response.data[0]["id"]

def buscar_perguntas_mais_frequentes():
    response = supabase.table("perguntas").select("pergunta").execute()
    perguntas = response.data
    perguntas_contadas = Counter([p['pergunta'].strip().lower() for p in perguntas])
    perguntas_frequentes = perguntas_contadas.most_common(5)
    perguntas_frequentes_formatadas = [(pergunta, count) for pergunta, count in perguntas_frequentes]
    return perguntas_frequentes_formatadas

notion_data = get_notion_data()

# Layout com o menu lateral
st.sidebar.title("Perguntas mais frequentes")
perguntas_frequentes = buscar_perguntas_mais_frequentes()
for pergunta, _ in perguntas_frequentes:
    st.sidebar.write(f"- {pergunta.capitalize()}")

# Interface principal
st.title(" 🤖 Assistente FABAPAR")
st.markdown('<p style="margin-bottom: 5px;">🧠 Tem uma dúvida? O assistente está aqui para esclarecer! ✨</p>', unsafe_allow_html=True)

if "query" not in st.session_state:
    st.session_state.query = ""

query = st.text_input("Digite sua pergunta...", key="query", placeholder="Digite sua pergunta...", label_visibility="hidden")

def typing_effect(text, delay=0.03):
    output = st.empty()
    for i in range(len(text)+1):
        output.markdown(f"{text[:i]}", unsafe_allow_html=True)
        time.sleep(delay)

if st.button("Perguntar", key="perguntar"):
    if query:
        resposta = ask_oracle(query, notion_data)
        st.write("### Resposta:")
        typing_effect(resposta)
        salvar_pergunta(query, resposta)

st.markdown(""" 
    --- 
    <p style="text-align: center; color: gray; font-size: 14px;">© 2025 Matheus Amaral. Todos os direitos reservados.</p>
""", unsafe_allow_html=True)

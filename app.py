import streamlit as st
import time
import json
from oraculo import ask_oracle, get_notion_data  # Importando a função get_notion_data
from datetime import datetime

# Função para salvar a pergunta no histórico
def salvar_pergunta(pergunta):
    try:
        # Verifica se o arquivo de histórico existe
        with open('historico_perguntas.json', 'r') as f:
            historico = json.load(f)
    except FileNotFoundError:
        historico = []

    # Adiciona a pergunta com o timestamp
    historico.append({
        'pergunta': pergunta,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    # Salva o histórico de volta no arquivo
    with open('historico_perguntas.json', 'w') as f:
        json.dump(historico, f, indent=4)

# Função para carregar o histórico de perguntas
def carregar_historico():
    try:
        with open('historico_perguntas.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

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

        # Salvar a pergunta no histórico
        salvar_pergunta(query)

        # Feedback do usuário
        feedback = st.radio("Avalie a resposta:", ("Útil", "Não útil"))

        if feedback:
            # Salvar o feedback em um arquivo ou banco de dados
            st.write(f"Obrigado pelo seu feedback: {feedback}!")
            with open("feedbacks.txt", "a") as file:
                file.write(f"Pergunta: {query}\nResposta: {resposta}\nFeedback: {feedback}\n\n")

st.markdown(""" 
    --- 
    <p style="text-align: center; color: gray; font-size: 14px;">© 2025 Matheus Amaral. Todos os direitos reservados.</p>
""", unsafe_allow_html=True)

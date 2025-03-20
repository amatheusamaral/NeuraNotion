import streamlit as st
import time
from oraculo import ask_oracle, get_notion_data  # Importando a função get_notion_data

# Carregar dados do Notion
notion_data = get_notion_data()

st.title(" 🤖 Assistente FABAPAR")
st.write("🧠 Tem uma dúvida? O assistente está aqui para esclarecer! Faça sua pergunta! ✨")

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


st.markdown("""
    ---
    <p style="text-align: center; color: gray; font-size: 14px;">© 2025 Matheus Amaral. Todos os direitos reservados.</p>
""", unsafe_allow_html=True)

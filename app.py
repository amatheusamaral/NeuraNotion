import streamlit as st
import time
from oraculo import ask_oracle, get_notion_data
from datetime import datetime
from supabase import create_client
from collections import Counter

SUPABASE_URL = "https://dlnkrqvdmqlvbywycvcl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsbmtycXZkbXFsdmJ5d3ljdmNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI4MjE5MTIsImV4cCI6MjA1ODM5NzkxMn0.fUY104cBJrV-Jk9P9Zix--zlNb9rLCzKrANU6xmSueQ"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Carregar os dados do Notion
notion_data = get_notion_data()

# Criar estado na sessão do Streamlit para controle de conversa
if "estado_conversa" not in st.session_state:
    st.session_state.estado_conversa = None  # Nenhuma conversa pendente
if "pergunta_pendente" not in st.session_state:
    st.session_state.pergunta_pendente = None  # Nenhuma pergunta pendente

# Função para salvar perguntas no Supabase
def salvar_pergunta(pergunta, resposta):
    data = {
        "pergunta": pergunta,
        "resposta": resposta,
        "timestamp": datetime.now().isoformat()
    }
    response = supabase.table("perguntas").insert(data).execute()
    return response.data[0]["id"]

# Definindo sugestões de perguntas manualmente com categorias
categorias_perguntas = {
    "RH": [
        "Quais são os benefícios oferecidos aos colaboradores?",
        "Como faço para atualizar meus dados cadastrais?",
        "Como consultar e agendar minhas férias?",
        "Como funciona o controle e registro do banco de horas?",
        "Quais cursos e treinamentos estão disponíveis para desenvolvimento profissional?",
        "Com quem posso falar em caso de dúvidas sobre folha de pagamento ou contrato?"
    ],
    "Processos": [
        "Qual é o horário de funcionamento dos setores administrativos?",
        "Onde posso acessar os documentos e procedimentos internos?",
        "Como funciona o fluxo de solicitação de serviços internos?",
        "Quais são os prazos para solicitações administrativas?",
        "Onde encontro os formulários institucionais?",
        "Como posso solicitar uso de salas ou recursos da instituição?"
    ],
    "TI": [
        "Como acesso o sistema acadêmico ou corporativo?",
        "Estou com problemas de acesso ao e-mail institucional, como resolver?",
        "Como solicito suporte técnico para computador ou impressora?",
        "O que fazer quando o Wi-Fi da instituição não está funcionando?",
        "Como redefinir minha senha do sistema?",
        "Quais softwares estão disponíveis para uso institucional?"
    ],
    "Comunicacao": [
        "Como solicitar a divulgação de eventos ou campanhas internas?",
        "Qual o procedimento para atualizar informações no site institucional?",
        "Onde posso enviar sugestões de conteúdo para redes sociais?",
        "Como entrar em contato com a equipe de comunicação?",
        "Quais são os canais oficiais de comunicação interna?",
        "Como posso participar das campanhas institucionais?"
    ]
}

# Layout com o menu lateral mais organizado
st.sidebar.title("Sugestões de Perguntas")
st.sidebar.markdown("""<style>.sidebar .sidebar-content {padding: 20px; background-color: #f0f2f6;}</style>""", unsafe_allow_html=True)

# Exibindo as sugestões de perguntas no menu lateral, organizadas por categorias com expanders
for categoria, perguntas in categorias_perguntas.items():
    with st.sidebar.expander(categoria, expanded=False):  # Expander para cada categoria
        for pergunta in perguntas:
            st.markdown(f"- {pergunta}")

# Interface principal
st.title(" 🤖 Assistente FABAPAR")
st.markdown('<p style="margin-bottom: 5px;">🧠 Tem uma dúvida? O assistente está aqui para esclarecer! ✨</p>', unsafe_allow_html=True)

query = st.text_input("Digite sua pergunta...", key="query", placeholder="Digite sua pergunta...", label_visibility="hidden")

# Função para mostrar o efeito de digitação
def typing_effect(text, delay=0.03):
    output = st.empty()
    for i in range(len(text) + 1):
        output.markdown(f"{text[:i]}", unsafe_allow_html=True)
        time.sleep(delay)

# Verifica se o modelo foi carregado e se os dados do Notion estão presentes
if not notion_data:
    st.warning("⚠️ Não foi possível carregar os dados do Notion.")
else:
    st.write("🔍 Dados do Notion carregados com sucesso!")

# Processando a pergunta do usuário
if st.button("Enviar", key="perguntar"):
    if query:
        resposta = ask_oracle(query, notion_data)
        st.write("### Resposta:")
        typing_effect(resposta)
        salvar_pergunta(query, resposta)

st.markdown("""
    --- 
    <p style="text-align: center; color: gray; font-size: 14px;">© 2025 Matheus Amaral. Todos os direitos reservados.</p>
""", unsafe_allow_html=True)

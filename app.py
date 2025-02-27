import streamlit as st
import sqlite3

# Conectando ao banco de dados SQLite
conn = sqlite3.connect("seguranca.db", check_same_thread=False)
cursor = conn.cursor()

# Criando as tabelas, caso não existam
cursor.execute("""
CREATE TABLE IF NOT EXISTS trabalhadores (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id TEXT NOT NULL,
    dispositivo_id INTEGER NOT NULL,
    local TEXT NOT NULL,
    data_ativacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (funcionario_id) REFERENCES trabalhadores(id)
)
""")
conn.commit()

# Definição dos dispositivos
dispositivos = {
    1: {"local": "Andar 1 - Sala de Reuniões"},
    2: {"local": "Andar 2 - Escritório de TI"},
    3: {"local": "Andar 3 - Área de Produção"},
    4: {"local": "Andar 4 - Refeitório"}
}

# Função para cadastrar trabalhador
def cadastrar_trabalhador(funcionario_id, nome):
    cursor.execute("INSERT INTO trabalhadores (id, nome) VALUES (?, ?)", (funcionario_id, nome))
    conn.commit()
    return f"Trabalhador {nome} com ID {funcionario_id} cadastrado com sucesso!"

# Função para registrar ativação
def registrar_ativacao(funcionario_id, dispositivo_id):
    dispositivo = dispositivos.get(dispositivo_id)
    if dispositivo:
        cursor.execute("SELECT nome FROM trabalhadores WHERE id = ?", (funcionario_id,))
        trabalhador = cursor.fetchone()
        if trabalhador:
            nome_trabalhador = trabalhador[0]
            cursor.execute("INSERT INTO registros (funcionario_id, dispositivo_id, local) VALUES (?, ?, ?)",
                           (funcionario_id, dispositivo_id, dispositivo["local"]))
            conn.commit()
            return f"Funcionário {nome_trabalhador} (ID: {funcionario_id}) ativou o dispositivo no {dispositivo['local']}."
    return "Dispositivo não encontrado ou ID de funcionário inválido."


# Criando menu de navegação lateral
st.sidebar.title("Menu de Navegação")
pagina = st.sidebar.selectbox("Escolha uma opção", ["Ativar Dispositivo", "Cadastrar Trabalhador"])

# 📌 **Tela de Ativação de Dispositivo**
if pagina == "Ativar Dispositivo":
    st.title("Ativação de Dispositivos de Segurança")
    st.write("Digite seu ID de Funcionário e clique no botão do dispositivo para registrar sua ativação.")

    funcionario_id = st.text_input("Digite seu ID de Funcionário para ativação", "")

    for dispositivo_id, dispositivo_info in dispositivos.items():
        local = dispositivo_info["local"]
        if st.button(f"Ativar Dispositivo - {local}", key=f"dispositivo_{dispositivo_id}"):
            if funcionario_id:
                cursor.execute("SELECT * FROM trabalhadores WHERE id = ?", (funcionario_id,))
                trabalhador = cursor.fetchone()
                if trabalhador:
                    resultado = registrar_ativacao(funcionario_id, dispositivo_id)
                    st.success(resultado)
                else:
                    st.error("ID de funcionário não encontrado. Cadastre-se primeiro.")
            else:
                st.error("Por favor, insira seu ID de Funcionário.")

# 📌 **Tela de Cadastro de Trabalhador**
elif pagina == "Cadastrar Trabalhador":
    st.title("Cadastro de Trabalhador")
    st.write("Insira o ID e Nome do trabalhador para cadastrá-lo no sistema.")

    funcionario_id_cadastro = st.text_input("ID do Funcionário para cadastro", "")
    nome_trabalhador = st.text_input("Nome do Trabalhador", "")

    if st.button("Cadastrar Trabalhador"):
        if funcionario_id_cadastro and nome_trabalhador:
            try:
                mensagem = cadastrar_trabalhador(funcionario_id_cadastro, nome_trabalhador)
                st.success(mensagem)
            except sqlite3.IntegrityError:
                st.error("Erro: Esse ID já está cadastrado. Escolha um ID único.")
        else:
            st.error("Por favor, insira o ID e o nome do trabalhador.")

# Fechando a conexão com o banco de dados
conn.close()

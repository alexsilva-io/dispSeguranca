import sqlite3
import streamlit as st

# Conectando ao banco de dados SQLite
conn = sqlite3.connect("seguranca.db", check_same_thread=False)
cursor = conn.cursor()

# Criando as tabelas, caso não existam
cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
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
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
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

# Função para cadastrar funcionário
def cadastrar_funcionario(funcionario_id, nome):
    cursor.execute("INSERT INTO funcionarios (id, nome) VALUES (?, ?)", (funcionario_id, nome))
    conn.commit()
    return f"Funcionário {nome} com ID {funcionario_id} cadastrado com sucesso!"

# Função para registrar ativação
def registrar_ativacao(funcionario_id, dispositivo_id):
    dispositivo = dispositivos.get(dispositivo_id)
    if dispositivo:
        cursor.execute("SELECT nome FROM funcionarios WHERE id = ?", (funcionario_id,))
        funcionario = cursor.fetchone()
        if funcionario:
            nome_funcionario = funcionario[0]
            cursor.execute("INSERT INTO registros (funcionario_id, dispositivo_id, local) VALUES (?, ?, ?)",
                           (funcionario_id, dispositivo_id, dispositivo["local"]))
            conn.commit()
            return f"Funcionário {nome_funcionario} (ID: {funcionario_id}) ativou o dispositivo no {dispositivo['local']}."
    return "Dispositivo não encontrado ou ID de funcionário inválido."

# Criando menu de navegação lateral
st.sidebar.title("Menu de Navegação")
pagina = st.sidebar.selectbox("Escolha uma opção", ["Ativar Dispositivo", "Cadastrar Funcionário"])

# 📌 **Tela de Ativação de Dispositivo**
if pagina == "Ativar Dispositivo":
    st.title("Ativação de Dispositivos de Segurança")
    st.write("Digite seu ID de Funcionário e clique no botão do dispositivo para registrar sua ativação.")

    funcionario_id = st.text_input("Digite seu ID de Funcionário para ativação", "")

    for dispositivo_id, dispositivo_info in dispositivos.items():
        local = dispositivo_info["local"]
        if st.button(f"Ativar Dispositivo - {local}", key=f"dispositivo_{dispositivo_id}"):
            if funcionario_id:
                cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (funcionario_id,))
                funcionario = cursor.fetchone()
                if funcionario:
                    resultado = registrar_ativacao(funcionario_id, dispositivo_id)
                    st.success(resultado)
                else:
                    st.error("ID de funcionário não encontrado. Cadastre-se primeiro.")
            else:
                st.error("Por favor, insira seu ID de Funcionário.")

# 📌 **Tela de Cadastro de Funcionário**
elif pagina == "Cadastrar Funcionário":
    st.title("Cadastro de Funcionário")
    st.write("Insira o ID e Nome do funcionário para cadastrá-lo no sistema.")

    funcionario_id_cadastro = st.text_input("ID do Funcionário para cadastro", "")
    nome_funcionario = st.text_input("Nome do Funcionário", "")

    if st.button("Cadastrar Funcionário"):
        if funcionario_id_cadastro and nome_funcionario:
            try:
                mensagem = cadastrar_funcionario(funcionario_id_cadastro, nome_funcionario)
                st.success(mensagem)
            except sqlite3.IntegrityError:
                st.error("Erro: Esse ID já está cadastrado. Escolha um ID único.")
        else:
            st.error("Por favor, insira o ID e o nome do funcionário.")

# Fechando a conexão com o banco de dados
conn.close()

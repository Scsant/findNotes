import streamlit as st
import zipfile
import io

# --- CSS e Estilo ---
st.markdown("""
    <style>
        .title {
            font-size: 38px;
            font-weight: 800;
            color: #00BFFF;
            margin-bottom: 10px;
        }

        .stButton>button {
            background-color: #00BFFF;
            color: white;
            padding: 0.6em 1.5em;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }

        textarea, input {
            background-color: #1e1e1e !important;
            color: white !important;
        }

        .uploadedFile {
            color: #00BFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📎 Extrator de Guias PDF por Fazenda</div>', unsafe_allow_html=True)

# --- Inicialização de estado ---
if 'pdfs_por_fazenda' not in st.session_state:
    st.session_state.pdfs_por_fazenda = {}

# --- Entrada: Nome da Fazenda ---
fazenda_nome = st.text_input("🏡 Nome da Fazenda").strip()

if fazenda_nome:
    # --- Upload de arquivos PDF ---
    uploaded_now = st.file_uploader(f"📂 Upload de PDFs para a Fazenda '{fazenda_nome}'", type="pdf", accept_multiple_files=True)

    if fazenda_nome not in st.session_state.pdfs_por_fazenda:
        st.session_state.pdfs_por_fazenda[fazenda_nome] = []

    if uploaded_now:
        arquivos_atuais = {f.name for f in st.session_state.pdfs_por_fazenda[fazenda_nome]}
        novos_arquivos = [f for f in uploaded_now if f.name not in arquivos_atuais]

        if novos_arquivos:
            st.session_state.pdfs_por_fazenda[fazenda_nome].extend(novos_arquivos)
            st.success(f"✅ {len(novos_arquivos)} novos arquivos adicionados para a fazenda '{fazenda_nome}'.")

    total_fazenda = st.session_state.pdfs_por_fazenda[fazenda_nome]
    st.markdown(f"### 📁 Arquivos acumulados para '{fazenda_nome}': {len(total_fazenda)}")

    # --- Entrada dos números de guias ---
    guia_input = st.text_area("📑 Digite os números das guias (ex: 101, 102 ou uma por linha)")

    if guia_input:
        # --- Tratamento de entrada ---
        guias_input_linhas = guia_input.replace(",", "\n").splitlines()
        guias = [g.strip() for g in guias_input_linhas if g.strip().isdigit()]
        guias = list(set(guias))  # Remove duplicatas

        filtrados_dict = {}
        guias_encontradas = set()

        for file in total_fazenda:
            for guia in guias:
                if file.name.endswith(f"{guia}.pdf"):
                    filtrados_dict[file.name] = file
                    guias_encontradas.add(guia)
                    break

        filtrados = list(filtrados_dict.values())
        guias_nao_encontradas = set(guias) - guias_encontradas

        st.markdown(f"### 📂 Arquivos encontrados: {len(filtrados)} de {len(total_fazenda)} carregados")
       

        if guias_nao_encontradas:
            with st.expander("🔍 Guias não encontradas"):
                st.code("\n".join(sorted(guias_nao_encontradas)))

        # --- Geração do ZIP ---
        if st.button("📦 Gerar ZIP com arquivos encontrados"):
            if filtrados:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for f in filtrados:
                        zf.writestr(f.name, f.read())
                zip_buffer.seek(0)

                st.download_button("📥 Baixar Arquivos ZIP", zip_buffer, file_name=f"{fazenda_nome}_guias.zip")
            else:
                st.warning("⚠️ Nenhuma guia correspondente encontrada.")
else:
    st.info("👈 Digite o nome da fazenda para começar.")

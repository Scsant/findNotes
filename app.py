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

st.markdown('<div class="title">📎 Extrator de Guias PDF</div>', unsafe_allow_html=True)

# --- Inicialização do estado ---
if 'pdfs_acumulados' not in st.session_state:
    st.session_state.pdfs_acumulados = []

# --- Upload de arquivos PDF ---
uploaded_now = st.file_uploader("📂 Upload de múltiplos PDFs (acumulativo)", type="pdf", accept_multiple_files=True)

if uploaded_now:
    st.session_state.pdfs_acumulados.extend(uploaded_now)
    st.success(f"{len(uploaded_now)} novos arquivos adicionados.")

# --- Arquivos acumulados no sistema ---
total_files = st.session_state.pdfs_acumulados
st.markdown(f"### 📁 Total de arquivos carregados: {len(total_files)}")

# --- Entrada dos números de guias ---
guia_input = st.text_area("📑 Digite os números das guias (ex: 505, 506 ou um por linha)")

# --- Lógica de busca e filtragem ---
if guia_input:
    guias = [g.strip() for g in guia_input.replace(",", "\n").splitlines() if g.strip().isdigit()]
    guias = list(set(guias))  # Eliminar duplicatas

    # Filtragem sem duplicação de arquivos
    filtrados_dict = {}
    guias_encontradas = set()

    for file in total_files:
        for guia in guias:
            if file.name.endswith(f"{guia}.pdf"):
                filtrados_dict[file.name] = file
                guias_encontradas.add(guia)
                break

    filtrados = list(filtrados_dict.values())
    guias_nao_encontradas = set(guias) - guias_encontradas

    st.markdown(f"### 📂 Arquivos encontrados: {len(filtrados)} de {len(total_files)} carregados")
    st.success(f"✅ {len(guias_encontradas)} guias encontradas de {len(guias)} solicitadas.")

    # Expandir lista de não encontrados
    if guias_nao_encontradas:
        with st.expander("🔍 Guias não encontradas"):
            st.code("\n".join(sorted(guias_nao_encontradas)))

    # Geração do ZIP
    if st.button("📦 Gerar ZIP com arquivos encontrados"):
        if filtrados:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in filtrados:
                    zf.writestr(f.name, f.read())
            zip_buffer.seek(0)

            st.download_button("📥 Baixar Arquivos ZIP", zip_buffer, file_name="guias_filtradas.zip")
        else:
            st.warning("⚠️ Nenhuma guia correspondente encontrada.")

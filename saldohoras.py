from datetime import date

import pandas as pd
import streamlit as st


MESES = [
    "Janeiro",
    "Fevereiro",
    "Marco",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
SERVIDORES = [
    "Selecione",
    "Servidor 1",
    "Servidor 2",
    "Servidor 3",
]


st.set_page_config(
    page_title="Saldo de Horas",
    page_icon=":clock3:",
    layout="wide",
)

st.title("Tabela Banco de Horas")

st.subheader("Filtros")

mes_atual_indice = date.today().month - 1
filtro_col1, filtro_col2, filtro_col3, filtro_col4 = st.columns(4)

with filtro_col1:
    mes = st.selectbox("Mes", MESES, index=mes_atual_indice)
with filtro_col2:
    servidor = st.selectbox("Nome do servidor", SERVIDORES)
with filtro_col3:
    saldo_horas = st.text_input("Saldo de horas", value="00:00")
with filtro_col4:
    expiram_mes = st.text_input("Expiram esse mes", value="00:00")

st.divider()

st.subheader("Tabela")

registro = {
    "Mes": mes,
    "Servidor": servidor,
    "Saldo de horas": saldo_horas,
    "Expiram esse mes": expiram_mes,
}

df = pd.DataFrame([registro])
st.dataframe(df, use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Baixar CSV",
    data=csv,
    file_name="banco_de_horas.csv",
    mime="text/csv",
)

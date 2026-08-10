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
    "BIGAIL TUPARI",
    "BRENNER GABRIEL DIAS CRISPIN",
    "CISLEY MUNIS SILVA",
    "Geovana Dos Santos Silva",
    "INGRID GRISOLIA CYPRIANO MENEGATT",
    "MARCELO ANTONIO ANSILAGO",
    "MARIA LUCIA FERREIRA SANTANA DA CRUZ",
    "REGINALDO MARCELO DA SILVA",
    "ROBSON TEOFILO VARGAS",
    "THIAGO DE OLIVEIRA ALVES",
]


def aplicar_mascara_hhmm(chave: str) -> None:
    valor = st.session_state.get(chave, "")
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())

    if len(digitos) >= 3:
        digitos = digitos[-4:]
        horas = digitos[:-2].zfill(2)
        minutos = digitos[-2:]
        st.session_state[chave] = f"{horas}:{minutos}"
    elif len(digitos) == 0:
        st.session_state[chave] = ""
    else:
        st.session_state[chave] = digitos


def eh_hhmm_valido(valor: str) -> bool:
    if len(valor) != 5 or valor[2] != ":":
        return False

    horas, minutos = valor.split(":")
    return horas.isdigit() and minutos.isdigit() and int(minutos) <= 59


for chave_hora in ("saldo_horas", "expiram_mes"):
    st.session_state.setdefault(chave_hora, "00:00")


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
    saldo_horas = st.text_input(
        "Saldo de horas",
        key="saldo_horas",
        max_chars=5,
        placeholder="HH:MM",
        on_change=aplicar_mascara_hhmm,
        args=("saldo_horas",),
    )
with filtro_col4:
    expiram_mes = st.text_input(
        "Expiram esse mes",
        key="expiram_mes",
        max_chars=5,
        placeholder="HH:MM",
        on_change=aplicar_mascara_hhmm,
        args=("expiram_mes",),
    )

if saldo_horas and not eh_hhmm_valido(saldo_horas):
    st.warning("Preencha o saldo de horas no formato HH:MM.")

if expiram_mes and not eh_hhmm_valido(expiram_mes):
    st.warning("Preencha as horas que expiram no formato HH:MM.")

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

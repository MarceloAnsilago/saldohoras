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
COLUNAS_TABELA = ["Mes", "Servidor", "Saldo de horas", "Expiram esse mes"]


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


def montar_registro() -> dict[str, str]:
    return {
        "Mes": st.session_state["mes"],
        "Servidor": st.session_state["servidor"],
        "Saldo de horas": st.session_state["saldo_horas"],
        "Expiram esse mes": st.session_state["expiram_mes"],
    }


def adicionar_registro() -> None:
    servidor = st.session_state["servidor"]
    saldo_horas = st.session_state["saldo_horas"]
    expiram_mes = st.session_state["expiram_mes"]

    if servidor == "Selecione":
        st.session_state["mensagem_erro"] = "Selecione o nome do servidor."
        return

    if not eh_hhmm_valido(saldo_horas):
        st.session_state["mensagem_erro"] = "Preencha o saldo de horas no formato HH:MM."
        return

    if not eh_hhmm_valido(expiram_mes):
        st.session_state["mensagem_erro"] = "Preencha as horas que expiram no formato HH:MM."
        return

    st.session_state["registros"].append(montar_registro())
    st.session_state["mensagem_erro"] = ""
    st.session_state["mensagem_sucesso"] = "Registro adicionado."


for chave_hora in ("saldo_horas", "expiram_mes"):
    st.session_state.setdefault(chave_hora, "00:00")

st.session_state.setdefault("registros", [])
st.session_state.setdefault("mensagem_erro", "")
st.session_state.setdefault("mensagem_sucesso", "")


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
    st.selectbox("Mes", MESES, index=mes_atual_indice, key="mes")
with filtro_col2:
    st.selectbox("Nome do servidor", SERVIDORES, key="servidor")
with filtro_col3:
    st.text_input(
        "Saldo de horas",
        key="saldo_horas",
        max_chars=5,
        placeholder="HH:MM",
        on_change=aplicar_mascara_hhmm,
        args=("saldo_horas",),
    )
with filtro_col4:
    st.text_input(
        "Expiram esse mes",
        key="expiram_mes",
        max_chars=5,
        placeholder="HH:MM",
        on_change=aplicar_mascara_hhmm,
        args=("expiram_mes",),
    )

saldo_horas = st.session_state["saldo_horas"]
expiram_mes = st.session_state["expiram_mes"]

if saldo_horas and not eh_hhmm_valido(saldo_horas):
    st.warning("Preencha o saldo de horas no formato HH:MM.")

if expiram_mes and not eh_hhmm_valido(expiram_mes):
    st.warning("Preencha as horas que expiram no formato HH:MM.")

st.button("Adicionar", type="primary", on_click=adicionar_registro)

if st.session_state["mensagem_erro"]:
    st.error(st.session_state["mensagem_erro"])

if st.session_state["mensagem_sucesso"]:
    st.success(st.session_state["mensagem_sucesso"])

st.divider()

st.subheader("Tabela")

df = pd.DataFrame(st.session_state["registros"], columns=COLUNAS_TABELA)
st.dataframe(df, use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Baixar CSV",
    data=csv,
    file_name="banco_de_horas.csv",
    mime="text/csv",
)

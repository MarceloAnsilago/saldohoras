from datetime import date, time, timedelta

import pandas as pd
import streamlit as st


JORNADA_PADRAO = timedelta(hours=8)
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
SALDOS_HORAS = [
    "00:00",
    "01:00",
    "02:00",
    "04:00",
    "08:00",
    "16:00",
    "24:00",
    "40:00",
]
HORAS_EXPIRAM = [
    "00:00",
    "01:00",
    "02:00",
    "04:00",
    "08:00",
    "16:00",
    "24:00",
    "40:00",
]


def para_timedelta(valor: time) -> timedelta:
    return timedelta(hours=valor.hour, minutes=valor.minute)


def formatar_saldo(delta: timedelta) -> str:
    sinal = "-" if delta.total_seconds() < 0 else ""
    segundos = abs(int(delta.total_seconds()))
    horas, resto = divmod(segundos, 3600)
    minutos = resto // 60
    return f"{sinal}{horas:02d}:{minutos:02d}"


def calcular_horas_trabalhadas(entrada, saida_almoco, volta_almoco, saida) -> timedelta:
    manha = para_timedelta(saida_almoco) - para_timedelta(entrada)
    tarde = para_timedelta(saida) - para_timedelta(volta_almoco)
    return manha + tarde


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
    saldo_horas = st.selectbox("Saldo de horas", SALDOS_HORAS)
with filtro_col4:
    expiram_mes = st.selectbox("Expiram esse mes", HORAS_EXPIRAM)

with st.sidebar:
    st.header("Jornada")
    jornada_horas = st.number_input("Horas por dia", min_value=0, max_value=24, value=8)
    jornada_minutos = st.number_input("Minutos por dia", min_value=0, max_value=59, value=0)
    jornada = timedelta(hours=jornada_horas, minutes=jornada_minutos)

st.subheader("Lancamento diario")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    data = st.date_input("Data")
with col2:
    entrada = st.time_input("Entrada", value=time(8, 0))
with col3:
    saida_almoco = st.time_input("Saida almoco", value=time(12, 0))
with col4:
    volta_almoco = st.time_input("Volta almoco", value=time(13, 0))
with col5:
    saida = st.time_input("Saida", value=time(17, 0))

horas_trabalhadas = calcular_horas_trabalhadas(entrada, saida_almoco, volta_almoco, saida)
saldo_dia = horas_trabalhadas - jornada

metricas = st.columns(3)
metricas[0].metric("Horas trabalhadas", formatar_saldo(horas_trabalhadas))
metricas[1].metric("Jornada prevista", formatar_saldo(jornada))
metricas[2].metric("Saldo do dia", formatar_saldo(saldo_dia))

st.divider()

st.subheader("Tabela")

registro = {
    "Mes": mes,
    "Servidor": servidor,
    "Saldo de horas": saldo_horas,
    "Expiram esse mes": expiram_mes,
    "Data": data.strftime("%d/%m/%Y"),
    "Entrada": entrada.strftime("%H:%M"),
    "Saida almoco": saida_almoco.strftime("%H:%M"),
    "Volta almoco": volta_almoco.strftime("%H:%M"),
    "Saida": saida.strftime("%H:%M"),
    "Horas trabalhadas": formatar_saldo(horas_trabalhadas),
    "Saldo": formatar_saldo(saldo_dia),
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

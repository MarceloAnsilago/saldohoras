from datetime import date
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


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


def remover_registro(indice: int) -> None:
    if 0 <= indice < len(st.session_state["registros"]):
        st.session_state["registros"].pop(indice)
        st.session_state["mensagem_erro"] = ""
        st.session_state["mensagem_sucesso"] = "Registro removido."


def gerar_linhas_relatorio(registros: list[dict[str, str]]) -> str:
    if not registros:
        return """
            <tr>
                <td colspan="4" class="empty">Nenhum registro adicionado.</td>
            </tr>
        """

    linhas = []
    for registro in registros:
        linhas.append(
            f"""
            <tr>
                <td>{escape(registro["Mes"])}</td>
                <td>{escape(registro["Servidor"])}</td>
                <td>{escape(registro["Saldo de horas"])}</td>
                <td>{escape(registro["Expiram esse mes"])}</td>
            </tr>
            """
        )
    return "\n".join(linhas)


def gerar_html_relatorio(registros: list[dict[str, str]]) -> str:
    linhas = gerar_linhas_relatorio(registros)
    return f"""
    <!doctype html>
    <html lang="pt-BR">
    <head>
        <meta charset="utf-8">
        <style>
            :root {{
                --border: #d1d5db;
                --line: #d8dde3;
                --header: #f5f6f8;
                --stripe: #f1f1f1;
                --text: #111827;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 24px;
                background: #f4f6f8;
                color: var(--text);
                font-family: "Segoe UI", Arial, sans-serif;
            }}

            .actions {{
                margin: 0 0 12px;
            }}

            .print-button {{
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background: #ffffff;
                color: #111827;
                cursor: pointer;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 14px;
            }}

            .sheet {{
                background: #f4f6f8;
                min-height: 790px;
                padding: 26px 0;
            }}

            .report-card {{
                width: 100%;
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 6px;
                box-shadow: 0 2px 5px rgba(17, 24, 39, 0.16);
                overflow: hidden;
            }}

            .report-title {{
                align-items: center;
                border-bottom: 1px solid var(--border);
                display: flex;
                font-size: 20px;
                font-weight: 700;
                gap: 8px;
                line-height: 1.2;
                padding: 15px 24px;
            }}

            .table-icon {{
                border: 2px solid #1f2933;
                border-radius: 2px;
                display: inline-grid;
                grid-template-columns: repeat(3, 6px);
                grid-template-rows: repeat(3, 6px);
                height: 22px;
                overflow: hidden;
                width: 22px;
            }}

            .table-icon span {{
                border-bottom: 1px solid #1f2933;
                border-right: 1px solid #1f2933;
            }}

            .table-icon span:nth-child(3n) {{
                border-right: 0;
            }}

            .table-icon span:nth-last-child(-n+3) {{
                border-bottom: 0;
            }}

            .table-wrap {{
                padding: 24px;
            }}

            table {{
                border-collapse: collapse;
                font-size: 20px;
                width: 100%;
            }}

            th {{
                background: var(--header);
                border-bottom: 1px solid #c7cbd1;
                color: #000000;
                font-weight: 700;
                padding: 11px 8px;
                text-align: left;
            }}

            td {{
                border-bottom: 1px solid var(--line);
                color: #000000;
                font-weight: 400;
                padding: 10px 8px;
                text-align: left;
            }}

            tbody tr:nth-child(odd) td {{
                background: var(--stripe);
            }}

            .empty {{
                color: #4b5563;
                font-size: 16px;
                text-align: center;
            }}

            @media print {{
                body {{
                    background: #ffffff;
                    padding: 0;
                }}

                .actions {{
                    display: none;
                }}

                .sheet {{
                    background: #f4f6f8;
                    min-height: 100vh;
                    padding: 26px 24px;
                }}

                .report-card {{
                    box-shadow: 0 2px 5px rgba(17, 24, 39, 0.16);
                }}

                @page {{
                    margin: 12mm;
                    size: A4 landscape;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="actions">
            <button class="print-button" onclick="window.print()">Imprimir relatorio</button>
        </div>
        <main class="sheet">
            <section class="report-card">
                <header class="report-title">
                    <span class="table-icon" aria-hidden="true">
                        <span></span><span></span><span></span>
                        <span></span><span></span><span></span>
                        <span></span><span></span><span></span>
                    </span>
                    Tabela Banco de Horas
                </header>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Mes</th>
                                <th>Servidor</th>
                                <th>Saldo de horas</th>
                                <th>Expiram esse mes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {linhas}
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </body>
    </html>
    """


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

if st.session_state["registros"]:
    opcoes_remocao = [
        f"{indice + 1} - {registro['Servidor']} - {registro['Mes']}"
        for indice, registro in enumerate(st.session_state["registros"])
    ]
    indice_remocao = st.selectbox("Linha para remover", range(len(opcoes_remocao)), format_func=opcoes_remocao.__getitem__)
    st.button(
        "Remover linha selecionada",
        on_click=remover_registro,
        args=(indice_remocao,),
    )

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Baixar CSV",
    data=csv,
    file_name="banco_de_horas.csv",
    mime="text/csv",
)

st.subheader("Relatorio para impressao")
components.html(
    gerar_html_relatorio(st.session_state["registros"]),
    height=760,
    scrolling=True,
)

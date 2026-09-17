from datetime import date, timedelta
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
EQUIPES = ["Equipe 1", "Equipe 2"]
COLUNAS_TABELA = ["Servidor", "Saldo ultimo mes", "Saldo de horas", "Expiram esse mes"]


def aplicar_mascara_hhmm(chave: str) -> None:
    valor = st.session_state.get(chave, "")
    digitos = "".join(caractere for caractere in valor if caractere.isdigit())

    if len(digitos) >= 3:
        digitos = digitos[-5:]
        horas = digitos[:-2].zfill(2)
        minutos = digitos[-2:]
        st.session_state[chave] = f"{horas}:{minutos}"
    elif len(digitos) == 0:
        st.session_state[chave] = ""
    else:
        st.session_state[chave] = digitos


def eh_hhmm_valido(valor: str) -> bool:
    if ":" not in valor:
        return False

    horas, minutos = valor.split(":")
    return (
        2 <= len(horas) <= 3
        and len(minutos) == 2
        and horas.isdigit()
        and minutos.isdigit()
        and int(minutos) <= 59
    )


def horas_para_minutos(valor: str) -> int:
    horas, minutos = valor.split(":")
    return int(horas) * 60 + int(minutos)


def tem_saldo_para_folga(*valores: str) -> bool:
    return any(
        eh_hhmm_valido(valor) and horas_para_minutos(valor) >= 6 * 60
        for valor in valores
    )


def legenda_folga_sem_ponto(registro: dict[str, str]) -> str:
    if tem_saldo_para_folga(registro["Saldo ultimo mes"]):
        return "Hab. folga sem ponto"
    return ""


def montar_registro() -> dict[str, str]:
    return {
        "Servidor": st.session_state["servidor"],
        "Saldo ultimo mes": st.session_state["saldo_ultimo_mes"],
        "Saldo de horas": st.session_state["saldo_horas"],
        "Expiram esse mes": st.session_state["expiram_mes"],
    }


def adicionar_registro() -> None:
    servidor = st.session_state["servidor"]
    saldo_ultimo_mes = st.session_state["saldo_ultimo_mes"]
    saldo_horas = st.session_state["saldo_horas"]
    expiram_mes = st.session_state["expiram_mes"]

    if servidor == "Selecione":
        st.session_state["mensagem_erro"] = "Selecione o nome do servidor."
        return

    if not eh_hhmm_valido(saldo_ultimo_mes):
        st.session_state["mensagem_erro"] = "Preencha o saldo ultimo mes no formato HH:MM ou HHH:MM."
        return

    if not eh_hhmm_valido(saldo_horas):
        st.session_state["mensagem_erro"] = "Preencha o saldo de horas no formato HH:MM ou HHH:MM."
        return

    if not eh_hhmm_valido(expiram_mes):
        st.session_state["mensagem_erro"] = "Preencha as horas que expiram no formato HH:MM ou HHH:MM."
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
                <td colspan="5" class="empty">Nenhum registro adicionado.</td>
            </tr>
        """

    linhas = []
    for registro in registros:
        linhas.append(
            f"""
            <tr>
                <td>{escape(registro["Servidor"])}</td>
                <td>{escape(registro["Saldo ultimo mes"])}</td>
                <td>{escape(registro["Saldo de horas"])}</td>
                <td>{escape(registro["Expiram esse mes"])}</td>
                <td>{escape(legenda_folga_sem_ponto(registro))}</td>
            </tr>
            """
        )
    return "\n".join(linhas)


def gerar_html_relatorio(registros: list[dict[str, str]]) -> str:
    linhas = gerar_linhas_relatorio(registros)
    mes = escape(st.session_state["mes"])
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
                padding: 0;
                background: #f1f3f5;
                color: var(--text);
                font-family: "Segoe UI", Arial, sans-serif;
            }}

            .actions {{
                margin: 12px 0 12px;
                padding: 0 2px;
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
                font-size: 16px;
                width: 100%;
            }}

            th {{
                background: var(--header);
                border-bottom: 1px solid #c7cbd1;
                color: #000000;
                font-weight: 700;
                padding: 9px 6px;
                text-align: left;
            }}

            td {{
                border-bottom: 1px solid var(--line);
                color: #000000;
                font-weight: 400;
                padding: 8px 6px;
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
                    Tabela Banco de Horas - {mes}
                </header>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Servidor</th>
                                <th>Saldo ultimo mes</th>
                                <th>Saldo de horas</th>
                                <th>Expiram esse mes</th>
                                <th>Legenda</th>
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


def listar_datas(inicio: date, fim: date) -> list[date]:
    quantidade_dias = (fim - inicio).days + 1
    return [inicio + timedelta(days=indice) for indice in range(quantidade_dias)]


def equipe_trabalha_no_periodo(equipe: str, periodo: int) -> bool:
    return (equipe == "Equipe 1" and periodo == 1) or (
        equipe == "Equipe 2" and periodo == 2
    )


def montar_dias_mapa_plantao() -> list[dict[str, str | bool]]:
    equipe = st.session_state["equipe_mapa_plantao"]
    periodos = [
        (
            1,
            st.session_state["data_inicial_mapa_plantao_col1"],
            st.session_state["data_final_mapa_plantao_col1"],
            equipe_trabalha_no_periodo(equipe, 1),
        ),
        (
            2,
            st.session_state["data_inicial_mapa_plantao_col2"],
            st.session_state["data_final_mapa_plantao_col2"],
            equipe_trabalha_no_periodo(equipe, 2),
        ),
    ]

    dias_por_data = {}
    for periodo, inicio, fim, trabalha in periodos:
        for dia in listar_datas(inicio, fim):
            dias_por_data[dia.isoformat()] = {
                "Periodo": periodo,
                "Trabalha": trabalha,
            }

    return [
        {"Data": data, **informacoes}
        for data, informacoes in sorted(dias_por_data.items())
    ]


def adicionar_mapa_plantao() -> None:
    servidor = st.session_state["servidor_mapa_plantao"]
    data_inicial_col1 = st.session_state["data_inicial_mapa_plantao_col1"]
    data_final_col1 = st.session_state["data_final_mapa_plantao_col1"]
    data_inicial_col2 = st.session_state["data_inicial_mapa_plantao_col2"]
    data_final_col2 = st.session_state["data_final_mapa_plantao_col2"]

    if servidor == "Selecione":
        st.session_state["mensagem_erro_mapa_plantao"] = "Selecione o nome do servidor."
        return

    if data_final_col1 < data_inicial_col1 or data_final_col2 < data_inicial_col2:
        st.session_state["mensagem_erro_mapa_plantao"] = "A data final deve ser igual ou posterior a data inicial."
        return

    if data_inicial_col2 <= data_final_col1:
        st.session_state["mensagem_erro_mapa_plantao"] = (
            "O segundo periodo deve iniciar depois do primeiro periodo."
        )
        return

    st.session_state["mapas_plantao"].append(
        {
            "Equipe": st.session_state["equipe_mapa_plantao"],
            "Servidor": servidor,
            "Dias": montar_dias_mapa_plantao(),
        }
    )
    st.session_state["mensagem_erro_mapa_plantao"] = ""
    st.session_state["mensagem_sucesso_mapa_plantao"] = "Mapa adicionado."


def remover_mapa_plantao(indice: int) -> None:
    if 0 <= indice < len(st.session_state["mapas_plantao"]):
        st.session_state["mapas_plantao"].pop(indice)
        st.session_state["mensagem_erro_mapa_plantao"] = ""
        st.session_state["mensagem_sucesso_mapa_plantao"] = "Mapa removido."


def normalizar_mapa_plantao(mapa: dict[str, object]) -> dict[str, object]:
    return {
        "Equipe": mapa.get("Equipe", "Equipe 1"),
        "Servidor": mapa.get("Servidor", ""),
        "Dias": mapa.get("Dias", []),
    }


def gerar_quadrados_mapa_plantao(dias_mapa: list[dict[str, object]], trabalha: bool) -> str:
    dias = []
    periodo_anterior = None

    for dia in dias_mapa:
        if dia["Trabalha"] != trabalha:
            continue

        data_formatada = str(date.fromisoformat(dia["Data"]).day)
        classe_quadrado = "square filled" if trabalha else "square"
        periodo = dia.get("Periodo")

        if periodo_anterior is not None and periodo != periodo_anterior:
            classe_quadrado += " second-period"

        periodo_anterior = periodo
        dias.append(
            f"""
            <span class="{classe_quadrado}">{escape(data_formatada)}</span>
            """
        )

    return "\n".join(dias)


def periodo_dos_quadrados(dias_mapa: list[dict[str, object]], trabalha: bool) -> str:
    for dia in dias_mapa:
        if dia["Trabalha"] == trabalha:
            return f"period-{dia.get('Periodo', 1)}"
    return "period-1"


def gerar_linhas_mapa_plantao(mapas: list[dict[str, object]]) -> str:
    if not mapas:
        return """
            <tr>
                <td colspan="3" class="empty">Nenhum mapa adicionado nesta equipe.</td>
            </tr>
        """

    linhas = []
    for mapa in mapas:
        mapa = normalizar_mapa_plantao(mapa)
        dias_trabalho = gerar_quadrados_mapa_plantao(mapa["Dias"], True)
        dias_folga = gerar_quadrados_mapa_plantao(mapa["Dias"], False)
        periodo_trabalho = periodo_dos_quadrados(mapa["Dias"], True)
        periodo_folga = periodo_dos_quadrados(mapa["Dias"], False)

        linhas.append(
            f"""
            <tr>
                <td class="server-name">{escape(mapa["Servidor"])}</td>
                <td class="days-cell">
                    <div class="days-grid {periodo_trabalho}">
                        {dias_trabalho}
                    </div>
                </td>
                <td class="days-cell">
                    <div class="days-grid {periodo_folga}">
                        {dias_folga}
                    </div>
                </td>
            </tr>
            """
        )

    return "\n".join(linhas)


def gerar_tabela_equipe_mapa_plantao(equipe: str, mapas: list[dict[str, object]]) -> str:
    linhas = gerar_linhas_mapa_plantao(mapas)
    return f"""
        <section class="team-section">
            <h2>{escape(equipe)}</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Servidor</th>
                            <th>Trabalha</th>
                            <th>Folga</th>
                        </tr>
                    </thead>
                    <tbody>
                        {linhas}
                    </tbody>
                </table>
            </div>
        </section>
    """


def gerar_html_mapa_plantao(mapas: list[dict[str, object]]) -> str:
    tabelas = "\n".join(
        gerar_tabela_equipe_mapa_plantao(
            equipe,
            [
                mapa
                for mapa in mapas
                if normalizar_mapa_plantao(mapa)["Equipe"] == equipe
            ],
        )
        for equipe in EQUIPES
    )
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
                --text: #111827;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                background: #f1f3f5;
                color: var(--text);
                font-family: "Segoe UI", Arial, sans-serif;
            }}

            .actions {{
                margin: 12px 0 12px;
                padding: 0 2px;
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
                background: #f1f3f5;
                min-height: 790px;
                padding: 0;
            }}

            .report-card {{
                width: 100%;
                background: transparent;
                border: 0;
                border-radius: 0;
                box-shadow: none;
                overflow: hidden;
            }}

            .report-title {{
                display: none;
            }}

            .table-wrap {{
                padding: 2px 0 0;
            }}

            .team-section {{
                margin-bottom: 18px;
            }}

            .team-section h2 {{
                background: #d9d9d9;
                border: 1px solid #aeb4bb;
                border-bottom: 0;
                color: #000000;
                font-size: 15px;
                margin: 0;
                padding: 7px 8px;
            }}

            table {{
                border-collapse: collapse;
                background: #ffffff;
                font-size: 14px;
                width: 100%;
            }}

            th {{
                background: #d9d9d9;
                border: 1px solid #aeb4bb;
                color: #000000;
                font-weight: 700;
                padding: 6px 8px;
                text-align: center;
            }}

            td {{
                border: 1px solid #d6dbe0;
                color: #000000;
                padding: 4px 4px;
                text-align: left;
                vertical-align: middle;
            }}

            .server-name {{
                font-weight: 400;
                width: 350px;
            }}

            .days-grid {{
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
                justify-content: center;
                width: 100%;
            }}

            .days-cell {{
                text-align: center;
            }}

            .square {{
                align-items: center;
                background: #ffffff;
                border: 1px solid #d5dce3;
                border-radius: 5px;
                color: #4b5563;
                display: inline-flex;
                font-size: 12px;
                height: 25px;
                justify-content: center;
                line-height: 1;
                min-width: 24px;
                padding: 0 6px;
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}

            .square.second-period {{
                margin-left: 14px;
            }}

            .square.second-period ~ .square.second-period {{
                margin-left: 0;
            }}

            .square.filled {{
                background: #111827;
                border-color: #111827;
                box-shadow: inset 0 0 0 999px #111827;
                color: #ffffff;
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}

            .empty {{
                color: #4b5563;
                font-size: 16px;
                text-align: center;
            }}

            @media print {{
                * {{
                    print-color-adjust: exact;
                    -webkit-print-color-adjust: exact;
                }}

                body {{
                    background: #ffffff;
                    padding: 0;
                }}

                .actions {{
                    display: none;
                }}

                .sheet {{
                    background: #f1f3f5;
                    min-height: 100vh;
                    padding: 0;
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
            <button class="print-button" onclick="window.print()">Imprimir mapa</button>
        </div>
        <main class="sheet">
            <section class="report-card">
                <header class="report-title">Mapa de Plantao</header>
                {tabelas}
            </section>
        </main>
    </body>
    </html>
    """


for chave_hora in ("saldo_ultimo_mes", "saldo_horas", "expiram_mes"):
    st.session_state.setdefault(chave_hora, "00:00")

st.session_state.setdefault("registros", [])
st.session_state.setdefault("mensagem_erro", "")
st.session_state.setdefault("mensagem_sucesso", "")
st.session_state.setdefault("mapas_plantao", [])
st.session_state.setdefault("equipe_mapa_plantao", EQUIPES[0])
st.session_state.setdefault("mensagem_erro_mapa_plantao", "")
st.session_state.setdefault("mensagem_sucesso_mapa_plantao", "")


st.set_page_config(
    page_title="Saldo de Horas",
    page_icon=":clock3:",
    layout="wide",
)

st.title("Tabela Banco de Horas")

aba_banco_horas, aba_mapa_plantao = st.tabs(
    ["Tabela Banco de Horas", "Mapa de Plantao"]
)

with aba_banco_horas:
    st.subheader("Filtros")

    mes_atual_indice = date.today().month - 1
    filtro_col1, filtro_col2, filtro_col3, filtro_col4, filtro_col5 = st.columns(5)

    with filtro_col1:
        st.selectbox("Mes", MESES, index=mes_atual_indice, key="mes")
    with filtro_col2:
        st.selectbox("Nome do servidor", SERVIDORES, key="servidor")
    with filtro_col3:
        st.text_input(
            "Saldo ultimo mes",
            key="saldo_ultimo_mes",
            max_chars=6,
            placeholder="HHH:MM",
            on_change=aplicar_mascara_hhmm,
            args=("saldo_ultimo_mes",),
        )
    with filtro_col4:
        st.text_input(
            "Expiram esse mes",
            key="expiram_mes",
            max_chars=6,
            placeholder="HHH:MM",
            on_change=aplicar_mascara_hhmm,
            args=("expiram_mes",),
        )
    with filtro_col5:
        st.text_input(
            "Saldo de horas",
            key="saldo_horas",
            max_chars=6,
            placeholder="HHH:MM",
            on_change=aplicar_mascara_hhmm,
            args=("saldo_horas",),
        )

    saldo_ultimo_mes = st.session_state["saldo_ultimo_mes"]
    saldo_horas = st.session_state["saldo_horas"]
    expiram_mes = st.session_state["expiram_mes"]

    if saldo_ultimo_mes and not eh_hhmm_valido(saldo_ultimo_mes):
        st.warning("Preencha o saldo ultimo mes no formato HH:MM ou HHH:MM.")

    if saldo_horas and not eh_hhmm_valido(saldo_horas):
        st.warning("Preencha o saldo de horas no formato HH:MM ou HHH:MM.")

    if expiram_mes and not eh_hhmm_valido(expiram_mes):
        st.warning("Preencha as horas que expiram no formato HH:MM ou HHH:MM.")

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
            f"{indice + 1} - {registro['Servidor']}"
            for indice, registro in enumerate(st.session_state["registros"])
        ]
        indice_remocao = st.selectbox(
            "Linha para remover",
            range(len(opcoes_remocao)),
            format_func=opcoes_remocao.__getitem__,
        )
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

with aba_mapa_plantao:
    st.subheader("Mapa de Plantao")

    mapa_col1, mapa_col2 = st.columns(2)

    with mapa_col1:
        with st.container(border=True):
            st.markdown("**Primeiro periodo**")
            periodo_1_col1, periodo_1_col2 = st.columns(2)
            with periodo_1_col1:
                st.date_input("Data inicial", key="data_inicial_mapa_plantao_col1")
            with periodo_1_col2:
                st.date_input("Data final", key="data_final_mapa_plantao_col1")

    with mapa_col2:
        with st.container(border=True):
            st.markdown("**Segundo periodo**")
            periodo_2_col1, periodo_2_col2 = st.columns(2)
            with periodo_2_col1:
                st.date_input("Data inicial", key="data_inicial_mapa_plantao_col2")
            with periodo_2_col2:
                st.date_input("Data final", key="data_final_mapa_plantao_col2")

    st.selectbox("Equipe", EQUIPES, key="equipe_mapa_plantao")
    st.selectbox("Nome do servidor", SERVIDORES, key="servidor_mapa_plantao")
    if st.session_state["equipe_mapa_plantao"] == "Equipe 1":
        st.caption("Primeiro periodo: trabalha | Segundo periodo: folga")
    else:
        st.caption("Primeiro periodo: folga | Segundo periodo: trabalha")

    st.button(
        "Adicionar",
        type="primary",
        key="adicionar_mapa_plantao",
        on_click=adicionar_mapa_plantao,
    )

    if st.session_state["mensagem_erro_mapa_plantao"]:
        st.error(st.session_state["mensagem_erro_mapa_plantao"])

    if st.session_state["mensagem_sucesso_mapa_plantao"]:
        st.success(st.session_state["mensagem_sucesso_mapa_plantao"])

    if st.session_state["mapas_plantao"]:
        opcoes_remocao_mapa = [
            (
                f"{indice + 1} - {normalizar_mapa_plantao(mapa)['Equipe']} - "
                f"{normalizar_mapa_plantao(mapa)['Servidor']}"
            )
            for indice, mapa in enumerate(st.session_state["mapas_plantao"])
        ]
        indice_remocao_mapa = st.selectbox(
            "Mapa para remover",
            range(len(opcoes_remocao_mapa)),
            format_func=opcoes_remocao_mapa.__getitem__,
            key="indice_remocao_mapa_plantao",
        )
        st.button(
            "Remover mapa selecionado",
            on_click=remover_mapa_plantao,
            args=(indice_remocao_mapa,),
            key="remover_mapa_plantao",
        )

    st.divider()

    st.subheader("Mapa para impressao")
    components.html(
        gerar_html_mapa_plantao(st.session_state["mapas_plantao"]),
        height=760,
        scrolling=True,
    )

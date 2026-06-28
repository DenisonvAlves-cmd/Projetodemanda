# =============================================================================
# PREVISOR DE DEMANDA SEMANAL — RESTAURANTE & PADARIA
# Aplicativo web em Python + Streamlit
# Ramo: Alimentação (restaurante, padaria, lanchonete, confeitaria)
# =============================================================================

# ETAPA 1 — IMPORTAÇÃO DAS BIBLIOTECAS
# Cada biblioteca tem uma função específica. Sem elas o app não roda.
# streamlit  → monta toda a interface visual (tela, botões, gráficos)
# pandas     → organiza os dados em tabelas
# numpy      → faz os cálculos matemáticos (médias, somas, regressão)
# plotly     → gera gráficos interativos que o usuário pode explorar

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =============================================================================
# ETAPA 2 — CONFIGURAÇÃO INICIAL DA PÁGINA
# Deve ser o PRIMEIRO comando Streamlit do arquivo.
# Define o título da aba, ícone e layout da tela.
# =============================================================================

st.set_page_config(
    page_title="Previsor de Demanda — Alimentação",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# ETAPA 3 — ESTILO VISUAL (CSS)
# Personalizamos cores, cartões e tipografia com CSS injetado via markdown.
# A paleta usa tons quentes (âmbar/terracota) que remetem ao ramo alimentício.
# =============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.block-container { padding-top: 1.4rem; }

/* Cartão de métrica */
.metric-card {
    background: #fff8f2;
    border: 1px solid #f0d9c4;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-label { font-size: 12px; color: #7a5c3a; font-weight: 500;
                text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 600; color: #3b1f0a; }
.metric-sub   { font-size: 11px; color: #a07850; margin-top: 3px; }

/* Caixa de recomendação gerencial */
.rec-box {
    border-left: 4px solid #c0622a;
    background: #fff3eb;
    border-radius: 0 10px 10px 0;
    padding: 1.1rem 1.3rem;
    font-size: 14.5px;
    line-height: 1.75;
    color: #2e1608;
}

/* Aviso educacional */
.warn-box {
    background: #fffae6;
    border: 1px solid #e8c840;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 13px;
    color: #6b5000;
    margin-top: 0.6rem;
}

/* Rótulo de seção */
.section-label {
    font-size: 11.5px;
    font-weight: 600;
    color: #a07850;
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: .6rem;
}

/* Cartão de comparação de método */
.method-card {
    background: #fff8f2;
    border: 1px solid #f0d9c4;
    border-radius: 10px;
    padding: .85rem 1rem;
    text-align: center;
}
.method-card.best { border: 1.5px solid #c0622a; background: #fff3eb; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ETAPA 4 — CATÁLOGO DE PRODUTOS DO RAMO ALIMENTÍCIO
# Ao invés de um campo genérico, o usuário escolhe uma categoria e um produto
# já pré-carregado com dados históricos realistas de um estabelecimento.
# Isso contextualiza o exercício para a realidade de restaurantes e padarias.
# =============================================================================

CATALOGO = {
    "🥖 Padaria / Confeitaria": {
        "Pão francês (kg/dia → semanas)": [48, 51, 47, 53, 50, 55, 52, 58, 54, 60, 57, 62],
        "Bolo de chocolate (un/semana)":  [12, 14, 11, 15, 13, 16, 14, 18, 15, 19, 17, 20],
        "Croissant (un/semana)":          [30, 32, 28, 35, 31, 36, 33, 38, 34, 40, 37, 42],
        "Salgado assado (dúzia/semana)":  [20, 22, 19, 24, 21, 25, 23, 27, 24, 28, 26, 30],
    },
    "🍽️ Restaurante / Lanchonete": {
        "Refeições servidas (semana)":    [280, 295, 270, 310, 290, 320, 305, 335, 315, 345, 330, 360],
        "Hambúrguer artesanal (un/sem)":  [80, 85, 78, 92, 83, 96, 88, 102, 93, 108, 100, 115],
        "Porção de fritas (un/sem)":      [110, 118, 105, 125, 112, 130, 120, 138, 128, 145, 135, 150],
        "Suco natural (litros/semana)":   [60, 64, 57, 68, 62, 72, 66, 78, 70, 82, 75, 88],
    },
    "☕ Cafeteria / Bistrô": {
        "Cappuccino (xícaras/semana)":    [95, 100, 90, 108, 98, 115, 105, 122, 110, 130, 118, 138],
        "Pão de queijo (un/semana)":      [140, 148, 133, 158, 145, 165, 155, 175, 162, 182, 170, 190],
        "Fatia de torta (un/semana)":     [25, 27, 23, 30, 26, 32, 28, 35, 30, 38, 33, 40],
        "Combo café da manhã (un/sem)":   [45, 48, 42, 52, 47, 56, 50, 61, 54, 65, 58, 70],
    },
}

# =============================================================================
# ETAPA 5 — FUNÇÕES DE PREVISÃO
# Cada função implementa um método matemático diferente.
# Recebem o histórico e retornam uma lista com as previsões futuras.
# =============================================================================

def metodo_ingenuo(hist: list, n: int) -> list:
    """
    MÉTODO INGÊNUO
    Previsão = última demanda observada (repetida n vezes).
    Exemplo: semana 12 teve 62 kg → previsão para sem 13, 14... = 62 kg.
    Serve como referência mínima — se outro método não bater esse,
    algo está errado.
    """
    return [hist[-1]] * n


def media_movel_simples(hist: list, janela: int, n: int) -> list:
    """
    MÉDIA MÓVEL SIMPLES (MMS)
    Previsão = média das últimas 'janela' semanas.
    Exemplo janela=3 com histórico [..., 57, 60, 62]:
      MMS = (57 + 60 + 62) / 3 = 59,7 kg
    Suaviza oscilações mas pode demorar a reagir a mudanças bruscas.
    """
    serie = list(hist)
    previsoes = []
    for _ in range(n):
        w = serie[-janela:]
        p = sum(w) / len(w)
        previsoes.append(p)
        serie.append(p)
    return previsoes


def media_movel_ponderada(hist: list, janela: int, n: int) -> list:
    """
    MÉDIA MÓVEL PONDERADA (MMP)
    Semanas mais recentes recebem peso maior.
    Pesos automáticos: 1, 2, 3, ..., janela (soma = janela*(janela+1)/2).
    Exemplo janela=3 pesos [1,2,3] total=6, histórico [..., 57, 60, 62]:
      MMP = (57×1 + 60×2 + 62×3) / 6 = 60,5 kg
    Reage mais rápido a tendências recentes que a MMS.
    """
    pesos = list(range(1, janela + 1))
    total = sum(pesos)
    serie = list(hist)
    previsoes = []
    for _ in range(n):
        w = serie[-janela:]
        p = sum(v * pw for v, pw in zip(w, pesos)) / total
        previsoes.append(p)
        serie.append(p)
    return previsoes


def suavizacao_exponencial(hist: list, alfa: float, n: int) -> list:
    """
    SUAVIZAÇÃO EXPONENCIAL (SE)
    Fórmula: F(t+1) = α × D(t) + (1-α) × F(t)
      D(t) = demanda real da semana atual
      F(t) = previsão que havia sido feita para essa semana
      α    = peso dado ao dado mais recente (0 a 1)
    α = 0,3 → reage moderadamente; α = 0,7 → reage rápido.
    Para o futuro, sem nova demanda real, a previsão fica constante.
    """
    f = hist[0]
    for d in hist[1:]:
        f = alfa * d + (1 - alfa) * f
    return [f] * n


def regressao_linear(hist: list, n: int) -> list:
    """
    REGRESSÃO LINEAR SIMPLES
    Encontra a linha reta y = a + b×x que melhor descreve a tendência.
      b (inclinação) = covariância(x,y) / variância(x)
      a (intercepto) = ȳ - b × x̄
    Se b > 0 → demanda crescente; b < 0 → demanda em queda.
    Ideal quando há tendência clara e contínua de subida ou queda.
    """
    x = np.arange(1, len(hist) + 1, dtype=float)
    y = np.array(hist, dtype=float)
    xm, ym = x.mean(), y.mean()
    b = np.sum((x - xm) * (y - ym)) / (np.sum((x - xm) ** 2) or 1)
    a = ym - b * xm
    return [max(0.0, a + b * (len(hist) + i)) for i in range(1, n + 1)]


# =============================================================================
# ETAPA 6 — CÁLCULO DO ERRO MÉDIO ABSOLUTO (MAE)
# O MAE mede, em média, o quanto cada método errou nas semanas passadas.
# Técnica: "walk-forward validation" — treinamos só com o passado
# e medimos o erro em cada semana que já conhecemos.
# Quanto MENOR o MAE, melhor o ajuste histórico do método.
# ATENÇÃO: menor MAE histórico NÃO garante melhor previsão futura.
# =============================================================================

def calcular_mae(hist: list, metodo: str, janela: int, alfa: float) -> float | None:
    erros = []
    inicio = max(janela, 3)
    for i in range(inicio, len(hist)):
        treino, real = hist[:i], hist[i]
        if metodo == "ingenuo":
            prev = treino[-1]
        elif metodo == "sma":
            w = treino[-janela:]
            prev = sum(w) / len(w)
        elif metodo == "wma":
            w = treino[-janela:]
            pesos = list(range(1, janela + 1))
            prev = sum(v * p for v, p in zip(w, pesos)) / sum(pesos)
        elif metodo == "exp":
            f = treino[0]
            for d in treino[1:]:
                f = alfa * d + (1 - alfa) * f
            prev = f
        elif metodo == "lr":
            x = np.arange(1, len(treino) + 1, dtype=float)
            y = np.array(treino, dtype=float)
            xm, ym = x.mean(), y.mean()
            b = np.sum((x - xm) * (y - ym)) / (np.sum((x - xm) ** 2) or 1)
            a = ym - b * xm
            prev = a + b * (len(treino) + 1)
        else:
            continue
        erros.append(abs(real - prev))
    return round(sum(erros) / len(erros), 1) if erros else None


# =============================================================================
# ETAPA 7 — DETECÇÃO DE TENDÊNCIA E SAZONALIDADE
# Compara a média da primeira metade com a segunda metade do histórico.
# Também calcula o coeficiente de variação para detectar alta irregularidade.
# O resultado alimenta a recomendação gerencial automaticamente.
# =============================================================================

def detectar_tendencia(hist: list) -> str:
    n    = len(hist)
    mid  = n // 2
    m1   = sum(hist[:mid]) / mid
    m2   = sum(hist[mid:]) / (n - mid)
    diff = (m2 - m1) / m1 * 100

    # Calcula o CV sobre os RESÍDUOS da tendência linear
    # (diferença entre cada valor real e o valor esperado pela reta)
    # Isso evita classificar crescimento estável como "irregular"
    x     = list(range(1, n + 1))
    xm    = sum(x) / n
    ym    = sum(hist) / n
    num   = sum((x[i] - xm) * (hist[i] - ym) for i in range(n))
    den   = sum((x[i] - xm) ** 2 for i in range(n))
    b     = num / den if den != 0 else 0
    a     = ym - b * xm

    # Resíduos = valor real - valor esperado pela reta
    residuos  = [hist[i] - (a + b * x[i]) for i in range(n)]
    media_res = sum(residuos) / n
    desvio_res = (sum((r - media_res) ** 2 for r in residuos) / n) ** 0.5
    cv_residuos = desvio_res / ym if ym else 0

    if cv_residuos > 0.15: return "irregular"
    if diff >  5:          return "crescimento"
    if diff < -5:          return "queda"
    return "estavel"


# =============================================================================
# ETAPA 8 — BARRA LATERAL (SIDEBAR): CONFIGURAÇÕES DO APP
# O usuário escolhe o segmento, produto, parâmetros e métodos ativos.
# Tudo que está dentro de "with st.sidebar:" aparece no painel lateral.
# =============================================================================

with st.sidebar:
    st.markdown("## 🍽️ Configurações")
    st.markdown("---")

    # Segmento e produto
    st.subheader("Estabelecimento")
    segmento = st.selectbox("Segmento", list(CATALOGO.keys()))
    produtos  = list(CATALOGO[segmento].keys())
    produto   = st.selectbox("Produto / item", produtos)

    st.markdown("---")

    # Semanas
    st.subheader("Período")
    n_hist = st.selectbox("Semanas de histórico", [8, 10, 12], index=2)
    n_prev = st.selectbox("Semanas a prever",     [2, 4, 6, 8], index=1)

    st.markdown("---")

    # Parâmetros dos métodos
    st.subheader("Parâmetros")
    janela = st.select_slider("Janela média móvel (semanas)", [2, 3, 4, 5], value=3)
    alfa   = st.select_slider(
        "Alfa (α) — suavização exponencial",
        [0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
        value=0.3,
        format_func=lambda x: f"{x:.1f}",
    )

    st.markdown("---")

    # Métodos ativos
    st.subheader("Métodos ativos")
    usar = {
        "ingenuo": st.checkbox("Ingênuo",                 value=True),
        "sma":     st.checkbox("Média Móvel Simples",     value=True),
        "wma":     st.checkbox("Média Móvel Ponderada",   value=True),
        "exp":     st.checkbox("Suavização Exponencial",  value=True),
        "lr":      st.checkbox("Regressão Linear",        value=True),
    }

    st.markdown("---")

    # Capacidade máxima de produção
    st.subheader("⚙️ Capacidade produtiva")
    usar_capacidade = st.checkbox("Ativar alerta de capacidade", value=False)
    capacidade_maxima = None
    if usar_capacidade:
        capacidade_maxima = st.number_input(
            "Capacidade máxima por semana",
            min_value=1.0,
            value=float(CATALOGO[segmento][produto][0]) * 1.5,
            step=1.0,
            help="Limite máximo que seu estabelecimento produz por semana (ex: capacidade do forno, da equipe, da cozinha)."
        )

    st.markdown("---")
    st.caption("📌 Os dados de exemplo são simulados com base em padrões reais do setor alimentício.")


# =============================================================================
# ETAPA 9 — CABEÇALHO PRINCIPAL
# Tudo fora do bloco sidebar aparece na área central da página.
# =============================================================================

st.title("🍽️ Previsor de Demanda Semanal")
st.markdown(
    "**Ramo:** Alimentação — Restaurante, Padaria, Cafeteria &nbsp;|&nbsp; "
    "Informe o histórico semanal e receba previsões com análise gerencial."
)
st.markdown("---")

# =============================================================================
# ETAPA 10 — ENTRADA DOS DADOS HISTÓRICOS
# Os campos são pré-carregados com dados realistas do produto selecionado.
# O usuário pode editar cada semana livremente.
# st.columns(4) divide a área em 4 colunas para caber mais campos por linha.
# =============================================================================

valores_padrao = CATALOGO[segmento][produto]

st.markdown('<div class="section-label">Demanda histórica semanal</div>', unsafe_allow_html=True)
st.caption(f"Produto: **{produto.split('(')[0].strip()}** — edite os valores conforme os dados reais do seu estabelecimento.")

cols = st.columns(4)
hist = []
for i in range(n_hist):
    with cols[i % 4]:
        val = st.number_input(
            f"Semana {i+1}",
            min_value=0.0,
            value=float(valores_padrao[i]) if i < len(valores_padrao) else float(valores_padrao[-1]),
            step=1.0,
            key=f"w{i}",
        )
        hist.append(val)

st.markdown("---")

# =============================================================================
# ETAPA 11 — BOTÃO PRINCIPAL
# Toda a lógica de cálculo e exibição fica dentro do bloco "if calcular:".
# Isso garante que o app só processa quando o usuário clicar no botão.
# =============================================================================

calcular = st.button("🔍 Calcular Previsão", type="primary")

if calcular:

    # --- Validações básicas ---
    if len(hist) < 4:
        st.error("Informe pelo menos 4 semanas de histórico."); st.stop()
    if sum(hist) == 0:
        st.error("Todos os valores são zero. Insira dados reais."); st.stop()
    if not any(usar.values()):
        st.error("Selecione ao menos um método de previsão."); st.stop()

    # =========================================================================
    # ETAPA 12 — CÁLCULO DAS PREVISÕES E ERROS
    # Para cada método ativo, chamamos a função correspondente e calculamos MAE.
    # Os resultados ficam em dois dicionários:
    #   previsoes[metodo] = [lista de valores futuros]
    #   maes[metodo]      = erro médio absoluto (float ou None)
    # =========================================================================

    NOMES = {
        "ingenuo": "Ingênuo",
        "sma":     "Média Móvel Simples",
        "wma":     "Média Móvel Ponderada",
        "exp":     "Suavização Exponencial",
        "lr":      "Regressão Linear",
    }
    CORES = {
        "ingenuo": "#aaa8a0",
        "sma":     "#185FA5",
        "wma":     "#3B6D11",
        "exp":     "#c0622a",
        "lr":      "#7b3f9e",
    }
    TRACOS = {
        "ingenuo": "dot",
        "sma":     "solid",
        "wma":     "dash",
        "exp":     "dashdot",
        "lr":      "longdash",
    }

    previsoes, maes = {}, {}
    funcoes = {
        "ingenuo": lambda h, n: metodo_ingenuo(h, n),
        "sma":     lambda h, n: media_movel_simples(h, janela, n),
        "wma":     lambda h, n: media_movel_ponderada(h, janela, n),
        "exp":     lambda h, n: suavizacao_exponencial(h, alfa, n),
        "lr":      lambda h, n: regressao_linear(h, n),
    }
    for m, ativo in usar.items():
        if not ativo: continue
        previsoes[m] = funcoes[m](hist, n_prev)
        maes[m]      = calcular_mae(hist, m, janela, alfa)

    tendencia   = detectar_tendencia(hist)
    media_hist  = sum(hist) / len(hist)
    maes_val    = {m: v for m, v in maes.items() if v is not None}
    melhor      = min(maes_val, key=maes_val.get) if maes_val else list(previsoes.keys())[0]

    # Rótulos das semanas
    rot_hist = [f"Sem {i+1}" for i in range(len(hist))]
    rot_prev = [f"Prev {len(hist)+i+1}" for i in range(n_prev)]

    # =========================================================================
    # ETAPA 13 — MÉTRICAS DE RESUMO
    # Quatro cartões com os números mais relevantes do período analisado.
    # =========================================================================

    nome_curto = produto.split("(")[0].strip()
    st.subheader(f"Resultado — {nome_curto}")

    unidade = produto.split("(")[-1].replace(")", "").strip() if "(" in produto else "un"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Demanda média histórica</div>
            <div class="metric-value">{media_hist:.1f}</div>
            <div class="metric-sub">{unidade}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Pico histórico</div>
            <div class="metric-value">{max(hist):.0f}</div>
            <div class="metric-sub">{unidade}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Vale histórico</div>
            <div class="metric-value">{min(hist):.0f}</div>
            <div class="metric-sub">{unidade}</div></div>""", unsafe_allow_html=True)
    with c4:
        prev_proxima = round(previsoes[melhor][0], 1)
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Previsão próxima semana</div>
            <div class="metric-value">{prev_proxima}</div>
            <div class="metric-sub">{unidade} · {NOMES[melhor]}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Badge de tendência
    BADGES = {
        "crescimento": "🟢 Tendência de crescimento — demanda subindo",
        "queda":       "🔴 Tendência de queda — demanda diminuindo",
        "estavel":     "🔵 Demanda estável — sem variação significativa",
        "irregular":   "🟡 Alta variação — demanda irregular",
    }
    st.info(BADGES[tendencia])
    st.markdown("---")

    # =========================================================================
    # ETAPA 14 — GRÁFICO INTERATIVO (PLOTLY)
    # go.Figure() cria o objeto do gráfico vazio.
    # fig.add_trace() adiciona cada série de dados.
    # A linha vertical separa visualmente histórico de previsão.
    # =========================================================================

    st.subheader("📈 Histórico e Previsão")

    fig = go.Figure()

    # Linha do histórico real
    fig.add_trace(go.Scatter(
        x=rot_hist, y=hist,
        name="Histórico real",
        mode="lines+markers",
        line=dict(color="#3b1f0a", width=2.5),
        marker=dict(size=6, color="#c0622a"),
    ))

    # Linhas de previsão de cada método ativo
    for m, vals in previsoes.items():
        x_plot = [rot_hist[-1]] + rot_prev           # conecta no último ponto real
        y_plot = [hist[-1]]     + vals
        fig.add_trace(go.Scatter(
            x=x_plot, y=y_plot,
            name=NOMES[m],
            mode="lines+markers",
            line=dict(color=CORES[m], width=1.8, dash=TRACOS[m]),
            marker=dict(size=5),
        ))

    # Linha vertical separando histórico e previsão
    fig.add_vline(
        x=len(rot_hist) - 1,
        line_dash="dot", line_color="#c0622a", line_width=1.2,
        annotation_text="→ início da previsão",
        annotation_position="top left",
        annotation_font_color="#c0622a",
    )

    # Fundo sombreado na área de previsão
    fig.add_vrect(
        x0=len(rot_hist) - 1, x1=len(rot_hist) + len(rot_prev) - 1,
        fillcolor="#fff3eb", opacity=0.4, layer="below", line_width=0,
    )

    fig.update_layout(
        height=440,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,253,249,0.8)",
            bordercolor="#f0d9c4",
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=40, b=120),
        xaxis_title="Semana",
        yaxis_title=f"Demanda ({unidade})",
        plot_bgcolor="#fffdf9",
        paper_bgcolor="#fffdf9",
        font=dict(family="DM Sans, sans-serif"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f0e4d4")
    fig.update_yaxes(showgrid=True, gridcolor="#f0e4d4")

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    # =========================================================================
    # ETAPA 15 — COMPARAÇÃO DE MÉTODOS (MAE)
    # Cada método é exibido em um cartão com seu erro médio e previsão.
    # O método com menor MAE é destacado com borda colorida.
    # =========================================================================

    st.subheader("⚖️ Comparação de Métodos")
    cols_m = st.columns(len(previsoes))
    for idx, (m, vals) in enumerate(previsoes.items()):
        best_css = "best" if m == melhor else ""
        mae_str  = f"{maes[m]:.1f}" if maes[m] else "—"
        with cols_m[idx]:
            st.markdown(f"""
            <div class="method-card {best_css}">
                <div class="metric-label">{NOMES[m]}</div>
                <div style="font-size:12px;color:#a07850;margin:3px 0">MAE: <strong>{mae_str}</strong></div>
                <div class="metric-value" style="font-size:20px">{round(vals[0], 1)}</div>
                <div class="metric-sub">{'🏆 menor erro' if m == melhor else 'próx. sem.'}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="warn-box">
        ⚠️ O MAE mede o erro histórico de cada método. Menor MAE histórico <strong>não garante</strong>
        a melhor previsão futura — fatores como feriados, promoções e sazonalidade podem
        alterar completamente a demanda real do seu estabelecimento.
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # =========================================================================
    # ETAPA 16 — TABELA DE PREVISÃO POR SEMANA
    # pd.DataFrame cria uma tabela com os resultados de todos os métodos.
    # st.dataframe exibe de forma interativa (com scroll e ordenação).
    # =========================================================================

    st.subheader("📋 Previsão semana a semana")
    tabela = {"Semana": rot_prev}
    for m, vals in previsoes.items():
        tabela[NOMES[m]] = [round(v, 1) for v in vals]
    df = pd.DataFrame(tabela).set_index("Semana")
    st.dataframe(df, use_container_width=True)

    with st.expander("Ver histórico completo"):
        df_h = pd.DataFrame({"Semana": rot_hist, f"Demanda real ({unidade})": hist}).set_index("Semana")
        st.dataframe(df_h, use_container_width=True)

    st.markdown("---")

    # =========================================================================
    # ETAPA 17 — RECOMENDAÇÃO GERENCIAL CONTEXTUALIZADA
    # O texto gerado considera o tipo de produto, a tendência detectada e
    # as características específicas do ramo alimentício (perecibilidade,
    # desperdício, capacidade de produção diária etc.).
    # =========================================================================

    st.subheader("💼 Recomendação Gerencial")

    max_prev = round(max(previsoes[melhor]), 1)

    RECS = {
        "crescimento": f"""
A demanda de **{nome_curto}** está em **crescimento**. A previsão aponta para até
**{max_prev} {unidade}** nas próximas semanas.

**Recomendações para o estabelecimento:**
- Ajuste o planejamento de produção (massa, ingredientes, fichas técnicas) antes da semana de pico.
- Antecipe a compra de insumos perecíveis com margem de segurança — mas sem exagerar para evitar desperdício.
- Avalie se a equipe atual comporta o aumento de produção sem queda de qualidade.
- Comunique o estoque de segurança para o responsável pelas compras com pelo menos 2 dias de antecedência.
        """,
        "queda": f"""
A demanda de **{nome_curto}** está em **queda**. Produzir acima da previsão pode
gerar **desperdício de alimentos** e aumento do custo por unidade.

**Recomendações para o estabelecimento:**
- Reduza gradualmente o volume de produção ou compra dos insumos correspondentes.
- Analise se a queda é temporária (fim de estação, feriado) ou estrutural (perda de clientes).
- Considere promoções ou combos para escoar o estoque atual e fidelizar clientes.
- Revise o mix de produtos — talvez outro item esteja crescendo e compensando essa queda.
        """,
        "irregular": f"""
A demanda de **{nome_curto}** apresenta **alta variação** entre semanas.
Isso é comum em alimentos sensíveis a eventos, clima e datas comemorativas.

**Recomendações para o estabelecimento:**
- Investigue se as semanas de pico coincidem com fins de semana, feriados ou datas especiais.
- Implemente um controle de desperdício semanal para entender o custo real da irregularidade.
- Mantenha um estoque de segurança moderado dos insumos de maior shelf life.
- Considere ajustar o cardápio sazonalmente, aproveitando os picos como oportunidade de receita.
        """,
        "estavel": f"""
A demanda de **{nome_curto}** está **estável**, com média de
**{media_hist:.1f} {unidade}/semana**.

**Recomendações para o estabelecimento:**
- Use a previsão como referência para manter um ciclo de compras e produção regular.
- Pequenas variações são esperadas — o estoque de segurança deve cobrir ≈ 10 a 15% acima da média.
- Revise a previsão a cada mês incorporando os dados mais recentes.
- Explore oportunidades de crescimento: novos sabores, combos ou canais de venda (delivery, atacado).
        """,
    }

    st.markdown(f"""<div class="rec-box">
        {RECS[tendencia].strip().replace(chr(10), '<br>')}
        <br><br>
        <span style="font-size:12px;color:#7a5c3a;">
        ⚠️ Previsão não é certeza. Fatores externos — clima, feriados, concorrência,
        campanhas de marketing — podem alterar a demanda real. Revise semanalmente.
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================================
    # ETAPA 18 — ESTOQUE DE SEGURANÇA
    # Fórmula: Estoque de Segurança = Z × Desvio Padrão da demanda histórica
    # Z = 1,65 para nível de serviço de 95% (padrão do setor alimentício)
    # Resultado: quanto produzir além da previsão para cobrir variações.
    # =========================================================================

    st.subheader("🛡️ Estoque de Segurança")

    # Cálculo do desvio padrão do histórico
    desvio_hist = float(np.std(hist))

    # Z = 1,65 → nível de serviço de 95%
    z = 1.65
    estoque_seg = round(z * desvio_hist, 1)

    prev_base = round(previsoes[melhor][0], 1)
    producao_recomendada = round(prev_base + estoque_seg, 1)

    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Previsão próxima semana</div>
            <div class="metric-value">{prev_base}</div>
            <div class="metric-sub">{unidade}</div></div>""", unsafe_allow_html=True)
    with cs2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Estoque de segurança (95%)</div>
            <div class="metric-value">{estoque_seg}</div>
            <div class="metric-sub">{unidade} adicionais</div></div>""", unsafe_allow_html=True)
    with cs3:
        st.markdown(f"""<div class="metric-card" style="border-color:#c0622a;">
            <div class="metric-label">Produção recomendada</div>
            <div class="metric-value" style="color:#c0622a;">{producao_recomendada}</div>
            <div class="metric-sub">{unidade} no total</div></div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="warn-box" style="margin-top:0.8rem">
        📦 <strong>Como interpretar:</strong> A previsão indica <strong>{prev_base} {unidade}</strong>.
        Somando o estoque de segurança de <strong>{estoque_seg} {unidade}</strong>
        (calculado com 95% de nível de serviço), a produção recomendada é de
        <strong>{producao_recomendada} {unidade}</strong> — cobrindo variações inesperadas
        sem gerar excesso de estoque.
    </div>""", unsafe_allow_html=True)

    # =========================================================================
    # ETAPA 19 — ALERTA DE CAPACIDADE MÁXIMA
    # Compara a produção recomendada com o limite informado pelo usuário.
    # Se ultrapassar, emite alerta vermelho com orientação gerencial.
    # =========================================================================

    if usar_capacidade and capacidade_maxima:
        st.markdown("---")
        st.subheader("⚙️ Alerta de Capacidade Produtiva")

        if producao_recomendada > capacidade_maxima:
            excesso = round(producao_recomendada - capacidade_maxima, 1)
            st.error(
                f"🚨 **Atenção:** A produção recomendada de **{producao_recomendada} {unidade}** "
                f"ultrapassa a capacidade máxima de **{capacidade_maxima:.0f} {unidade}** "
                f"em **{excesso} {unidade}**.\n\n"
                f"**Ações sugeridas:**\n"
                f"- Avalie ampliar a capacidade (mais turnos, equipamentos ou funcionários).\n"
                f"- Priorize os itens de maior margem caso não seja possível produzir tudo.\n"
                f"- Comunique o risco de ruptura de estoque ao gestor responsável."
            )
        elif producao_recomendada > capacidade_maxima * 0.90:
            st.warning(
                f"⚠️ **Atenção:** A produção recomendada de **{producao_recomendada} {unidade}** "
                f"está próxima do limite de capacidade de **{capacidade_maxima:.0f} {unidade}** "
                f"({round(producao_recomendada/capacidade_maxima*100)}% da capacidade).\n\n"
                f"Monitore de perto — pequenas variações na demanda podem ultrapassar o limite."
            )
        else:
            st.success(
                f"✅ A produção recomendada de **{producao_recomendada} {unidade}** está "
                f"dentro da capacidade de **{capacidade_maxima:.0f} {unidade}** "
                f"({round(producao_recomendada/capacidade_maxima*100)}% da capacidade utilizada)."
            )



# =============================================================================
# FIM DO ARQUIVO app.py
#
# Para rodar:
#   pip install -r requirements.txt
#   python -m streamlit run app.py
#
# O navegador abrirá em: http://localhost:8501
# =============================================================================

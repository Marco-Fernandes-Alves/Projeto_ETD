import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Moda & Mercados | Analytics Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Estilo de fundo e fontes */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
        font-family: 'Outfit', 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Cartões Bento */
    .bento-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    .bento-card:hover {
        transform: translateY(-2px);
        border-color: #4f46e5;
    }
    
    /* Indicadores numéricos */
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #6366f1;
        margin-top: 8px;
    }
    .metric-label {
        font-size: 14px;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEMANA_4_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(SEMANA_4_DIR, "outputs", "moda_analytics.db")

@st.cache_data
def carregar_dados_analiticos():
    """Carrega dados consolidados da View no SQLite com cópia automática inteligente se corrido individualmente."""
    if not os.path.exists(DB_PATH):
        PROJETO_DIR = os.path.dirname(SEMANA_4_DIR)
        src_db = os.path.join(PROJETO_DIR, "Semana_3", "outputs", "moda_analytics.db")
        if os.path.exists(src_db):
            try:
                os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
                import shutil
                shutil.copy(src_db, DB_PATH)
            except Exception:
                pass
                
    if not os.path.exists(DB_PATH):
        st.error(f"Base de dados SQLite não encontrada em {DB_PATH}. Por favor, executa o pipeline primeiro!")
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM view_analitica_consolidada ORDER BY date ASC"
    df = pd.read_query(query, conn) if hasattr(pd, 'read_query') else pd.read_sql(query, conn)
    conn.close()
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Preencher nulos nas colunas de fecho e volume (devido a feriados intercalados nas bolsas)
    colunas_mercado = ['nike_close', 'nike_volume', 'lvmh_close', 'lvmh_volume', 'inditex_close', 'inditex_volume']
    for col in colunas_mercado:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').ffill().bfill()
            
    return df

df = carregar_dados_analiticos()

if not df.empty:
    st.sidebar.markdown("<h2 style='text-align: center; color: #6366f1;'>👗 Filtros Analíticos</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    min_date = df['date'].min().to_pydatetime()
    max_date = df['date'].max().to_pydatetime()
    
    import datetime
    # Por defeito mostramos todo o histórico temporal para povoar ricamente todos os gráficos financeiros e macroeconómicos (FRED)
    default_start = min_date
        
    datas_selecionadas = st.sidebar.slider(
        "Selecione o Intervalo Temporal",
        min_value=min_date,
        max_value=max_date,
        value=(default_start, max_date),
        format="DD/MM/YYYY"
    )
    
    st.sidebar.info("💡 **Dica**: A recolha de notícias de sentimento está concentrada no período recente (finais de Abril a meados de Maio de 2026). Ajuste o slider temporal para esse intervalo caso pretenda focar a análise no impacto de sentimento.")

    
    st.sidebar.markdown("### Seleção de Portfólio")
    marcas = {
        "Nike Inc. (NKE)": "nike_close",
        "LVMH Group (LVMUY)": "lvmh_close",
        "Inditex S.A. / Zara (INDITEX)": "inditex_close"
    }
    marcas_selecionadas = st.sidebar.multiselect(
        "Marcas a Visualizar",
        options=list(marcas.keys()),
        default=list(marcas.keys())
    )
    
    st.sidebar.markdown("### Sentimento das Notícias")
    filtro_sentimento = st.sidebar.selectbox(
        "Filtrar por Impacto de Sentimento",
        options=["Todos", "Sentimento Positivo (> 0.1)", "Sentimento Neutro", "Sentimento Negativo (< -0.1)"]
    )
    
    mask = (df['date'] >= datas_selecionadas[0]) & (df['date'] <= datas_selecionadas[1])
    df_filtrado = df[mask].copy()
    
    if filtro_sentimento == "Sentimento Positivo (> 0.1)":
        df_filtrado = df_filtrado[df_filtrado['sentiment_score'] > 0.1]
    elif filtro_sentimento == "Sentimento Negativo (< -0.1)":
        df_filtrado = df_filtrado[df_filtrado['sentiment_score'] < -0.1]
    elif filtro_sentimento == "Sentimento Neutro":
        df_filtrado = df_filtrado[(df_filtrado['sentiment_score'] >= -0.1) & (df_filtrado['sentiment_score'] <= 0.1)]

    st.markdown("<h1 style='text-align: center; background: linear-gradient(to right, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Fashion Retail & Industry Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 30px;'>Cruzamento analítico de performance financeira de gigantes da moda, consumo a retalho e sentimento mediático do setor.</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        venda_media = df_filtrado['vendas_vestuario'].mean()
        st.markdown(f"""
        <div class="bento-card">
            <div class="metric-label">Vendas Médias Mensais (FRED)</div>
            <div class="metric-value">${venda_media:,.2f}M</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        inf_media = df_filtrado['inflacao_vestuario'].mean()
        st.markdown(f"""
        <div class="bento-card">
            <div class="metric-label">Inflação Média Setorial (FRED)</div>
            <div class="metric-value">{inf_media:.2f} pts</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        sent_medio = df_filtrado['sentiment_score'].mean()
        cor_sent = "#22c55e" if sent_medio > 0.05 else ("#ef4444" if sent_medio < -0.05 else "#94a3b8")
        st.markdown(f"""
        <div class="bento-card">
            <div class="metric-label">Sentimento Médio do Setor</div>
            <div class="metric-value" style="color: {cor_sent};">{sent_medio:+.3f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        reg_count = len(df_filtrado)
        st.markdown(f"""
        <div class="bento-card">
            <div class="metric-label">Dias Úteis Mapeados</div>
            <div class="metric-value" style="color: #a855f7;">{reg_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Performance de Mercado Normalizada (Base 100)")
    st.markdown("<p style='color: #94a3b8;'>Permite a comparação direta de performance entre gigantes com diferentes preços de cotação de mercado, utilizando as cotações normalizadas no início do período.</p>", unsafe_allow_html=True)
    
    if marcas_selecionadas:
        fig_acoes = go.Figure()
        
        for m_nome in marcas_selecionadas:
            col_id = marcas[m_nome]
            
            first_val = df_filtrado[col_id].iloc[0] if len(df_filtrado) > 0 else 1.0
            normalizada = (df_filtrado[col_id] / first_val) * 100
            
            fig_acoes.add_trace(go.Scatter(
                x=df_filtrado['date'],
                y=normalizada,
                mode='lines',
                name=m_nome,
                line=dict(width=3)
            ))
            
        fig_acoes.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#334155'),
            yaxis=dict(title="Índice Base 100", showgrid=True, gridcolor='#334155'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_acoes, use_container_width=True)
    else:
        st.warning("Selecione pelo menos uma marca na barra lateral para analisar a cotação.")

    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown("### 🛍️ Consumo a Retalho vs. Performance das Marcas")
        st.markdown("<p style='color: #94a3b8;'>Análise de correlação entre vendas mensais (FRED) e o valor consolidado de portfólio.</p>", unsafe_allow_html=True)
        
        df_filtrado['portfolio_index'] = (
            df_filtrado['nike_close'] * 0.4 + 
            df_filtrado['lvmh_close'] * 0.4 + 
            df_filtrado['inditex_close'] * 0.2
        )
        
        fig_corr = px.scatter(
            df_filtrado,
            x="vendas_vestuario",
            y="portfolio_index",
            color="sentiment_score",
            color_continuous_scale=px.colors.diverging.Tealrose,
            labels={"vendas_vestuario": "Vendas a Retalho FRED ($M)", "portfolio_index": "Preço do Portfólio ($)", "sentiment_score": "Sentimento"},
            trendline="ols",
            trendline_color_override="#6366f1"
        )
        fig_corr.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#334155'),
            yaxis=dict(showgrid=True, gridcolor='#334155')
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
    with g2:
        st.markdown("### 📰 Impacto do Sentimento nos Volumes de Negociação")
        st.markdown("<p style='color: #94a3b8;'>Cruzamento das flutuações de sentimento mediático sobre tendências/sustentabilidade com volumes diários.</p>", unsafe_allow_html=True)
        
        df_filtrado['sent_cat'] = pd.cut(
            df_filtrado['sentiment_score'],
            bins=[-1, -0.15, 0.15, 1],
            labels=['Negativo', 'Neutro', 'Positivo']
        )
        
        sent_volume = df_filtrado.groupby('sent_cat', observed=False)['nike_volume'].mean().reset_index()
        
        fig_sent = px.bar(
            sent_volume,
            x="sent_cat",
            y="nike_volume",
            color="sent_cat",
            color_discrete_map={'Negativo': '#ef4444', 'Neutro': '#94a3b8', 'Positivo': '#22c55e'},
            labels={"sent_cat": "Categoria de Sentimento", "nike_volume": "Volume Médio de Negociação (NKE)"}
        )
        fig_sent.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#334155'),
            showlegend=False
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("### 💸 Dinâmica de Custo de Vida vs Consumo no Setor de Vestuário")
    
    fig_macro = go.Figure()
    fig_macro.add_trace(go.Scatter(
        x=df_filtrado['date'],
        y=df_filtrado['vendas_vestuario'],
        name="Vendas Retalho FRED ($M)",
        line=dict(color='#38bdf8', width=3)
    ))
    fig_macro.add_trace(go.Scatter(
        x=df_filtrado['date'],
        y=df_filtrado['inflacao_vestuario'] * 200,  
        name="Índice de Inflação FRED (Escalado)",
        line=dict(color='#f43f5e', width=3, dash='dash')
    ))
    
    fig_macro.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#334155'),
        yaxis=dict(showgrid=True, gridcolor='#334155'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_macro, use_container_width=True)

    st.markdown("### 🎙️ Análise Comparativa do Sentimento de Notícias por Marca")
    st.markdown("<p style='color: #94a3b8;'>Evolução do sentimento de notícias específico para a Nike, LVMH e Inditex/Zara gerado de forma autónoma via API local.</p>", unsafe_allow_html=True)
    
    fig_sent_brand = go.Figure()
    
    if 'nike_sentiment' in df_filtrado.columns and "Nike Inc. (NKE)" in marcas_selecionadas:
        fig_sent_brand.add_trace(go.Scatter(
            x=df_filtrado['date'],
            y=df_filtrado['nike_sentiment'],
            name="Sentimento Nike",
            line=dict(color='#6366f1', width=3)
        ))
        
    if 'lvmh_sentiment' in df_filtrado.columns and "LVMH Group (LVMUY)" in marcas_selecionadas:
        fig_sent_brand.add_trace(go.Scatter(
            x=df_filtrado['date'],
            y=df_filtrado['lvmh_sentiment'],
            name="Sentimento LVMH",
            line=dict(color='#eab308', width=3)
        ))
        
    if 'inditex_sentiment' in df_filtrado.columns and "Inditex S.A. / Zara (INDITEX)" in marcas_selecionadas:
        fig_sent_brand.add_trace(go.Scatter(
            x=df_filtrado['date'],
            y=df_filtrado['inditex_sentiment'],
            name="Sentimento Inditex/Zara",
            line=dict(color='#10b981', width=3)
        ))
        
    if 'sentiment_score' in df_filtrado.columns:
        fig_sent_brand.add_trace(go.Scatter(
            x=df_filtrado['date'],
            y=df_filtrado['sentiment_score'],
            name="Sentimento Geral do Setor",
            line=dict(color='#94a3b8', width=1.5, dash='dash')
        ))

        
    fig_sent_brand.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#334155'),
        yaxis=dict(title="Score de Sentimento", showgrid=True, gridcolor='#334155'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_sent_brand, use_container_width=True)

else:
    st.warning("Sem dados suficientes carregados para gerar visualizações analíticas.")

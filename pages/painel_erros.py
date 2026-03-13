"""
pages/painel_erros.py – Error / exception panel

Charts: Bar  – Erros por Tipo
        Line – Erros por Dia
        Table – Detalhe de erros
"""
import streamlit as st
import pandas as pd

from components.ui_components import (
    page_header, date_filter, metric_row,
    bar_chart, line_chart, donut_chart, styled_table, csv_uploader,
)
from components.data_loader import load_cargas, load_pallets, load_conferencia, load_caixa_hora, load_montagem_transporte, load_erros, load_erros_percentual
from pages.painel_geral import TIPO_PALETE_totals

GREEN    = "#2e7d32"
GREEN_LT = "#66bb6a"
RED      = "#c62828"

COLORS = [RED, GREEN]
COLORS_BAR = [GREEN, RED]

df_pallets = load_pallets()
df_cargas  = load_cargas()
df_conferencia = load_conferencia()
df_caixa_hora = load_caixa_hora()
df_montagem_transporte = load_montagem_transporte()
df_erros = load_erros()
df_erros_percentual = load_erros_percentual()

# ── Sidebar filters ───────────────────────────────────────────────────────
# Use a single date picker for all charts (same period applied across datasets)
df_pallets, period = date_filter(df_pallets, col="DATA_ENTREGA", key_prefix="period")
start, end = period

# Apply the same date range to other tables
if not df_cargas.empty and "delivery_date" in df_cargas.columns:
    mask_cargas = (df_cargas["delivery_date"].dt.date >= start) & (df_cargas["delivery_date"].dt.date <= end)
    df_cargas = df_cargas[mask_cargas]

if not df_conferencia.empty and "data_entrega" in df_conferencia.columns:
    mask_conf = (df_conferencia["data_entrega"].dt.date >= start) & (df_conferencia["data_entrega"].dt.date <= end)
    df_conferencia = df_conferencia[mask_conf]

if not df_caixa_hora.empty and "DATA_ENTREGA" in df_caixa_hora.columns:
    mask_caixa_hora = (df_caixa_hora["DATA_ENTREGA"].dt.date >= start) & (df_caixa_hora["DATA_ENTREGA"].dt.date <= end)
    df_caixa_hora = df_caixa_hora[mask_caixa_hora]

if not df_montagem_transporte.empty and "DATA_ENTREGA" in df_montagem_transporte.columns:
    mask_montagem = (df_montagem_transporte["DATA_ENTREGA"].dt.date >= start) & (df_montagem_transporte["DATA_ENTREGA"].dt.date <= end)
    df_montagem_transporte = df_montagem_transporte[mask_montagem]

if not df_erros.empty and "DATA_ENTREGA" in df_erros.columns:
    mask_erros = (df_erros["DATA_ENTREGA"].dt.date >= start) & (df_erros["DATA_ENTREGA"].dt.date <= end)
    df_erros = df_erros[mask_erros]



# ── Charts ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Percentual de Erros Total</div>', unsafe_allow_html=True)
    # if not df_erros_percentual.empty and "status" in df_erros_percentual.columns and "totais" in df_erros_percentual.columns:
        # erros_row = df_erros_percentual[df_erros_percentual["status"] == "ERROS"]
        # corretos_row = df_erros_percentual[df_erros_percentual["status"] == "CORRETOS"]
        # if not erros_row.empty and not corretos_row.empty:
    labels = df_erros_percentual["STATUS"].tolist()
    values = df_erros_percentual["TOTAIS"].tolist()
    
    fig = donut_chart(
        labels=labels,
        values=values,
        colors=COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Produtos com Mais Erros</div>', unsafe_allow_html=True)
    if not df_erros.empty and "PRODUTO" in df_erros.columns:
        produtos = (
            df_erros.groupby("PRODUTO").size().reset_index(name="TOTAL")
            .sort_values("TOTAL", ascending=True)
        )
        fig = bar_chart(produtos, x="TOTAL", y="PRODUTO", orientation="h")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Dados de erros indisponíveis")
    st.markdown('</div>', unsafe_allow_html=True)


# ── Table ────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Detalhe de Erros</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
if not df_erros.empty:
    styled_table(df_erros)
else:
    st.write("Dados de erros indisponíveis")
st.markdown('</div>', unsafe_allow_html=True)


# ── Additional Analysis ───────────────────────────────────────────────────
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Erros por Tipo</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if not df_erros.empty and "TIPO_ERRO" in df_erros.columns:
        tipo_erros = (
            df_erros.groupby("TIPO_ERRO").size().reset_index(name="TOTAL")
            .sort_values("TOTAL", ascending=False)
        )
        fig = bar_chart(tipo_erros, x="TIPO_ERRO", y="TOTAL", orientation="v")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Dados de erros indisponíveis")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Erros Informados pelos Conferentes</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if not df_erros.empty and "INFORMANTE" in df_erros.columns and "PERFIL_OFENSOR" in df_erros.columns:
        montadores = df_erros[df_erros["PERFIL_OFENSOR"] == "Montador"]
        if not montadores.empty:
            informantes = (
                montadores.groupby("INFORMANTE").size().reset_index(name="TOTAL")
                .sort_values("TOTAL", ascending=False)
                .rename(columns={"INFORMANTE": "CONFERENTE"})
            )
            # st.metric(label="Total Informantes", value=len(informantes))
            styled_table(informantes)
        else:
            st.write("Nenhum dado para Montadores")
    else:
        st.write("Dados de erros indisponíveis")
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Erros por Montador</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if not df_erros.empty and "OFENSOR" in df_erros.columns and "PERFIL_OFENSOR" in df_erros.columns:
        montadores = df_erros[df_erros["PERFIL_OFENSOR"] == "Montador"]
        if not montadores.empty:
            ofensores = (
                montadores.groupby("OFENSOR").size().reset_index(name="TOTAL")
                .sort_values("TOTAL", ascending=False)
                .rename(columns={"OFENSOR": "MONTADOR"})
            )
            styled_table(ofensores)
        else:
            st.write("Nenhum dado para Montadores")
    else:
        st.write("Dados de erros indisponíveis")
    st.markdown('</div>', unsafe_allow_html=True)


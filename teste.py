import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# 1. Carrega o CSV (depois do upload)
file = st.file_uploader("📁 Envie o arquivo de vendas (.csv)", type=['csv'])

if file:
    df_vendas = pd.read_csv(file, sep=';')

    # 2. Converte datas e ordena
    df_vendas['data_dia'] = pd.to_datetime(df_vendas['data_dia'])
    df_vendas = df_vendas.sort_values('data_dia').reset_index(drop=True)

    # 3. Garante que as vendas estão em formato numérico
    df_vendas['total_venda_dia_kg'] = pd.to_numeric(df_vendas['total_venda_dia_kg'], errors='coerce')
    df_vendas = df_vendas.dropna(subset=['total_venda_dia_kg'])

    # 4. Inicializa colunas auxiliares
    df_vendas['remanescente'] = 0.0
    df_vendas['demanda_real'] = 0.0

    # 5. Aplica lógica de remanescente e demanda
    for i in range(1, len(df_vendas)):
        venda_hoje = df_vendas.loc[i, 'total_venda_dia_kg']
        venda_ontem = df_vendas.loc[i - 1, 'total_venda_dia_kg']
        vendido_percent = venda_hoje / venda_ontem if venda_ontem > 0 else 1
        remanescente = venda_ontem * (1 - vendido_percent)
        df_vendas.loc[i, 'remanescente'] = remanescente
        df_vendas.loc[i, 'demanda_real'] = venda_hoje + remanescente

    df_vendas.loc[0, 'demanda_real'] = df_vendas.loc[0, 'total_venda_dia_kg']

    # 6. Calcula previsão com média móvel de 3 dias
    df_vendas['previsao_3dias'] = df_vendas['demanda_real'].rolling(window=3).mean()

    # Gráfico da demanda real ao longo do tempo
fig_demanda = px.line(df_vendas, x='data_dia', y='demanda_real', title='Demanda Real por Dia')
st.plotly_chart(fig_demanda)

# Gráfico da previsão de 3 dias
fig_previsao = px.line(df_vendas, x='data_dia', y='previsao_3dias', title='Previsão de Demanda (Média Móvel de 3 dias)')
st.plotly_chart(fig_previsao)

# Gráfico combinado de demanda real e previsão
fig_combinado = px.line(df_vendas, x='data_dia', y=['demanda_real', 'previsao_3dias'], title='Demanda Real x Previsão')
st.plotly_chart(fig_combinado)

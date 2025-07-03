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

   # 6. Previsão de 3 dias (média móvel)
df_vendas['previsao_3dias_kg'] = df_vendas['demanda_real'].rolling(window=3).mean()

# 7. Previsão diária simples (igual à demanda do dia anterior)
df_vendas['previsao_dia_kg'] = df_vendas['demanda_real'].shift(1)

# 8. Arredondar todas as colunas relevantes para 2 casas decimais
colunas_kg = ['total_venda_dia_kg', 'remanescente', 'demanda_real', 'previsao_3dias_kg', 'previsao_dia_kg']
df_vendas[colunas_kg] = df_vendas[colunas_kg].round(2)

# 9. Renomear colunas para exibir "kg"
df_exibir = df_vendas.rename(columns={
    'demanda_real': 'Demanda Real (kg)',
    'previsao_3dias_kg': 'Previsão 3 Dias (kg)',
    'previsao_dia_kg': 'Previsão Diária (kg)',
    'total_venda_dia_kg': 'Venda Real (kg)',
    'remanescente': 'Remanescente (kg)'
})

st.subheader("📈 Gráfico 1: Demanda Real (kg)")
fig1 = px.line(df_exibir, x='data_dia', y='Demanda Real (kg)', markers=True,
               title='Demanda Real por Dia (kg)')
st.plotly_chart(fig1)

st.subheader("📉 Gráfico 2: Previsão Diária (kg)")
fig2 = px.line(df_exibir, x='data_dia', y='Previsão Diária (kg)', markers=True,
               title='Previsão Diária por Dia (kg)')
st.plotly_chart(fig2)

st.subheader("🔮 Gráfico 3: Previsão de 3 Dias (kg)")
fig3 = px.line(df_exibir, x='data_dia', y='Previsão 3 Dias (kg)', markers=True,
               title='Previsão Média Móvel de 3 Dias (kg)')
st.plotly_chart(fig3)

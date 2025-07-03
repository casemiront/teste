import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# 1. Carrega o CSV (depois do upload no Colab)
file = st.file_uploader("📁 Envie o arquivo de vendas (.csv)", type=['csv'])

if file:
    df_vendas = pd.read_csv(file, sep=';')
    # ... continue o processamento normalmente
else:
    st.warning("Por favor, envie um arquivo CSV para começar.")

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

# 7. Exibe o resultado
print(df_vendas[['data_dia', 'demanda_real', 'previsao_3dias']])

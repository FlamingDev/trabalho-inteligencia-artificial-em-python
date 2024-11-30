import streamlit as st
import pandas as pd
import altair as alt
import time
from model import Planet

# Título e parâmetros iniciais
st.title("Modelo Baseado em Agentes")
num_ticks = st.slider("Selecione o número de passos:", min_value=1, max_value=100, value=50)
altura = st.slider("Selecione a altura", min_value=10, max_value=50, step=5, value=15)
largura = st.slider("Selecione a largura", min_value=10, max_value=50, step=5, value=20)
n_resources = st.sidebar.slider("Número de Recursos", 1, 50, 10)
n_obstacles = st.sidebar.slider("Número de Obstáculos", 0, 20, 5)
n_SA = st.sidebar.slider("Agentes Simples", 0, 20, 5)
n_SBA = st.sidebar.slider("Agentes Baseados em Estado", 0, 20, 5)
n_OBA = st.sidebar.slider("Agentes Baseados em Objetivo", 0, 20, 5)

# Inicializa o modelo ao clicar no botão "Rodar Simulação"
if "model" not in st.session_state:
    st.session_state["model"] = None
    st.session_state["step_count"] = 0

if st.button("Rodar simulação"):
    modelo = Planet(
        n_SA=n_SA,
        n_SBA=n_SBA,
        n_OBA=n_OBA,
        height=altura,
        width=largura,
        n_resources=n_resources,
        n_obstacles=n_obstacles,
        base_pos=(0, 0)
    )
    st.session_state["model"] = modelo
    st.session_state["step_count"] = 0

# Recupera o modelo do estado
model = st.session_state["model"]

# Executa apenas se o modelo foi inicializado
if model:

# Cria um espaço reservado para o gráfico

    chart_placeholder = st.empty()

   
    
    # Laço para executar a simulação automaticamente
    while st.session_state["step_count"] < num_ticks:
        # Executa o passo no modelo
        model.step()
        st.session_state["step_count"] += 1

        # Atualiza o DataFrame e renderiza o gráfico
        df = model.to_dataframe()
        

        chart = alt.Chart(df).mark_point(filled=True, size=100).encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=[0, largura - 1], nice=False), axis=alt.Axis(tickMinStep=1)),  # Passos de 1
            y=alt.Y("y:Q", scale=alt.Scale(domain=[0, altura - 1], nice=False), axis=alt.Axis(tickMinStep=1)),  # Passos de 1
            color=alt.Color("color:N", legend=None),
            shape=alt.Shape("shape:N", legend=None),
            tooltip=["type"]
        ).properties(
            width=600,
            height=600
        )

        # Atualiza o gráfico no espaço reservado
        chart_placeholder.altair_chart(chart, use_container_width=True)

        # Pausa antes do próximo passo
        time.sleep(1)  

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración básica (Streamlit usará su modo oscuro por defecto)
st.set_page_config(page_title="Monitor de Aislamiento IP/DAR", layout="wide")

st.title("Monitor de Resistencia vs Corriente de Fuga (IP/DAR)")
st.write("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Parámetros del Ensayo")
    v_test = st.number_input("Voltaje de Prueba (V)", value=1000)
    r_final = st.slider("Resistencia Final Estimada (MΩ)", 100, 10000, 5000)
    k = st.slider("Constante de Absorción (Curvatura)", 0.1, 2.0, 0.5)

# --- CÁLCULOS ---
t = np.linspace(0.1, 10, 500) 
r_t = r_final * (1 - np.exp(-k * t)) + (r_final * 0.1) 
i_total = v_test / r_t

r_05 = np.interp(0.5, t, r_t)
r_1 = np.interp(1.0, t, r_t)
r_10 = np.interp(10.0, t, r_t)

dar = r_1 / r_05
ip = r_10 / r_1

# --- MÉTRICAS ---
st.header("Resultados Calculados")
col1, col2, col3, col4 = st.columns(4)
col1.metric("R @ 1 min", f"{int(r_1)} MΩ")
col2.metric("R @ 10 min", f"{int(r_10)} MΩ")
col3.metric("DAR (R1 / R0.5)", f"{dar:.2f}")
col4.metric("IP (R10 / R1)", f"{ip:.2f}")

st.write("---")

# --- GRÁFICO EN MODO OSCURO ---
st.header("Curvas de Ensayo de Aislamiento")

fig = go.Figure()

# Resistencia (Azul claro para que resalte en negro)
fig.add_trace(go.Scatter(x=t, y=r_t, name="Resistencia (MΩ)", line=dict(color='#00BFFF', width=4)))

# Corriente (Rojo, línea discontinua)
fig.add_trace(go.Scatter(x=t, y=i_total, name="Corriente (µA)", yaxis="y2", line=dict(color='#FF4136', width=4, dash='dash')))

# Configuración del diseño
fig.update_layout(
    template="plotly_dark", # El secreto para que se vea bien en negro
    xaxis=dict(title="Tiempo (Minutos)", dtick=1),
    yaxis=dict(title="Resistencia (MΩ)", color="#00BFFF", type="log"),
    yaxis2=dict(title="Corriente (µA)", color="#FF4136", overlaying="y", side="right", type="log"),
    legend=dict(x=0.8, y=0.1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

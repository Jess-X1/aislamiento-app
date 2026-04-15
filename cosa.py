import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Monitor de Aislamiento IP/DAR", layout="wide")

st.title("⚡ Monitor de Resistencia vs Corriente de Fuga (IP/DAR)")
st.markdown("Simulador basado en datos reales de campo. Introduce el R1 medido y ajusta el perfil de absorción.")
st.write("---")

# --- BARRA LATERAL (Con la lógica corregida) ---
with st.sidebar:
    st.header("Datos de Campo")
    
    # El voltaje solo sirve para calcular la corriente, no afecta el IP
    v_test = st.number_input("Voltaje de Prueba (V)", value=1000, step=500)
    
    # AQUÍ ESTÁ TU IDEA: Pedimos R1 en lugar de la resistencia final
    r_1_input = st.number_input("Resistencia a 1 minuto (MΩ) - R1", value=1500, step=100)
    
    st.markdown("---")
    st.header("Perfil del Aislante")
    # Renombrado para que el jefe entienda que ESTO es lo que mueve el IP/DAR
    k = st.slider("Curvatura (Modifica el IP / DAR)", min_value=0.01, max_value=2.0, value=0.5, step=0.05,
                  help="Valores bajos = Curva plana (IP bajo, mal aislamiento). Valores altos = Curva pronunciada (IP alto, buen aislamiento).")

# --- CÁLCULOS (Ingeniería Inversa para que la curva pase por R1) ---
t = np.linspace(0.1, 10, 500) 

# Si sabemos R1, calculamos cuál debería ser R_final matemáticamente para que la curva cuadre
r_final = r_1_input / ((1 - np.exp(-k * 1.0)) + 0.1)

# Ahora sí, generamos la curva completa
r_t = r_final * (1 - np.exp(-k * t)) + (r_final * 0.1) 
i_total = v_test / r_t

# Interpolar puntos clave
r_05 = np.interp(0.5, t, r_t)
r_1 = np.interp(1.0, t, r_t) # Esto siempre será igual a r_1_input
r_10 = np.interp(10.0, t, r_t)

dar = r_1 / r_05
ip = r_10 / r_1

# --- MÉTRICAS ---
st.header("Resultados Calculados")
col1, col2, col3, col4 = st.columns(4)
col1.metric("R @ 1 min", f"{int(r_1)} MΩ")
col2.metric("R @ 10 min", f"{int(r_10)} MΩ")

# Colores dinámicos para que el jefe vea si el IP es bueno o malo
ip_color = "normal" if ip >= 2.0 else "inverse" # Inverse lo pone rojo en Streamlit
col3.metric("DAR (R1 / R0.5)", f"{dar:.2f}")
col4.metric("IP (R10 / R1)", f"{ip:.2f}", delta="Revisar" if ip < 2.0 else "OK", delta_color=ip_color)

st.write("---")

# --- GRÁFICO EN MODO OSCURO ---
st.header("Curvas de Ensayo de Aislamiento")

fig = go.Figure()

# Resistencia
fig.add_trace(go.Scatter(x=t, y=r_t, name="Resistencia (MΩ)", line=dict(color='#00BFFF', width=4)))

# Corriente 
fig.add_trace(go.Scatter(x=t, y=i_total, name="Corriente (µA)", yaxis="y2", line=dict(color='#FF4136', width=4, dash='dash')))

fig.update_layout(
    template="plotly_dark",
    xaxis=dict(title="Tiempo (Minutos)", dtick=1),
    yaxis=dict(title="Resistencia (MΩ)", color="#00BFFF", type="log"),
    yaxis2=dict(title="Corriente (µA)", color="#FF4136", overlaying="y", side="right", type="log"),
    legend=dict(x=0.8, y=0.1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

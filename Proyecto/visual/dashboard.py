import streamlit as st

# Configurar la página
st.set_page_config(
    page_title="Sistema de Simulación de Drones",
    layout="wide",
    page_icon="🚁"
)

# ===== ESTILO PERSONALIZADO (CSS) =====
st.markdown("""
    <style>
        .main {
            background-color: #0f1116;
            color: #FFFFFF;
        }
        h1, h2, h3, h4, h5 {
            color: #FAFAFA;
        }
        .metric-container {
            display: flex;
            justify-content: space-between;
            margin-top: 1rem;
        }
        .metric-box {
            background-color: #1e222f;
            padding: 20px;
            border-radius: 12px;
            width: 32%;
            text-align: center;
            box-shadow: 0 0 10px rgba(0,0,0,0.4);
        }
        .metric-box h3 {
            margin: 0;
            color: #66d9ef;
        }
        .metric-box p {
            font-size: 1.5rem;
            margin: 5px 0 0 0;
        }
    </style>
""", unsafe_allow_html=True)

# ===== ENCABEZADO =====
st.markdown("<h1 style='text-align: center;'>🚁 Sistema de Simulación de Drones</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #888;'>Correos Chile - Plataforma de Simulación</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)


# ===== MÉTRICAS COMO TARJETAS =====
st.markdown("""
<div class="metric-container">
    <div class="metric-box">
        <h3>📦 Almacenamiento</h3>
        <p>20%</p>
    </div>
    <div class="metric-box">
        <h3>🔋 Recarga</h3>
        <p>20%</p>
    </div>
    <div class="metric-box">
        <h3>👤 Clientes</h3>
        <p>60%</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ===== TABS =====
tabs = st.tabs(["🎮 Simulación", "📡 Red de Nodos", "📋 Pedidos", "🚦 Rutas", "📈 Estadísticas"])


# ===== TAB 1 - Simulación =====
with tabs[0]:
    st.subheader("🎮 Parámetros de la Simulación")

    col1, col2, col3 = st.columns(3)

    with col1:
        number_of_nodes = st.slider("🔢 Nodos totales", 10, 150, 30)
    with col2:
        number_of_edges = st.slider("🔗 Conexiones (aristas)", 10, 300, 60)
    with col3:
        number_of_orders = st.slider("📦 Pedidos", 1, 500, 25)

    # Cálculos derivados
    client_nodes = int(0.6 * number_of_nodes)
    storage_nodes = int(0.2 * number_of_nodes)
    recharge_nodes = number_of_nodes - client_nodes - storage_nodes

    st.markdown("---")
    st.markdown("### 🧠 Distribución Calculada:")

    st.markdown(f"- 👤 Clientes: **{client_nodes}**")
    st.markdown(f"- 📦 Almacenamiento: **{storage_nodes}**")
    st.markdown(f"- 🔋 Recarga: **{recharge_nodes}**")

    st.markdown("")

    if st.button("🚀 Ejecutar Simulación"):
        st.success("✅ Simulación iniciada correctamente.")
        st.session_state.sim_started = True

    if st.session_state.get("sim_started"):
        st.info("📡 Simulación activa...")


# ===== PLACEHOLDERS PARA OTRAS TABS =====
with tabs[1]:
    st.subheader("📡 Red de Nodos")
    st.warning("🌐 Módulo de visualización de red próximamente...")

with tabs[2]:
    st.subheader("📋 Pedidos y Clientes")
    st.warning("📦 Visualización de pedidos en desarrollo.")

with tabs[3]:
    st.subheader("🚦 Análisis de Rutas")
    st.warning("🛣️ Aquí podrás ver rutas optimizadas y resultados logísticos.")

with tabs[4]:
    st.subheader("📈 Estadísticas")
    st.warning("📊 Módulo de estadísticas generales próximamente.")

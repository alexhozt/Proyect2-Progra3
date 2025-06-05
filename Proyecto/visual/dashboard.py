import streamlit as st
import random

from model.graph import Node, Edge, Graph




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
        
        def generate_unique_ids(n):
            """
            Genera hasta n IDs únicos tipo Excel (A, B, ..., Z, AA, AB, ..., AZ, ..., AAA, etc.)
            """
            ids = []
            i = 0
            while len(ids) < n:
                s = ""
                temp = i
                while True:
                    s = chr(ord('A') + temp % 26) + s
                    temp = temp // 26 - 1
                    if temp < 0:
                        break
                ids.append(s)
                i += 1
            return ids
        
        def generate_graph(n_nodes, n_edges, client_ratio=0.6, storage_ratio=0.2):
            graph = Graph()

            roles = (
                ['cliente'] * int(n_nodes * client_ratio) +
                ['almacenamiento'] * int(n_nodes * storage_ratio) +
                ['recarga'] * (n_nodes - int(n_nodes * client_ratio) - int(n_nodes * storage_ratio))
            )
            random.shuffle(roles)

            ids = generate_unique_ids(n_nodes)
            node_map = {}

            for i in range(n_nodes):
                node = Node(ids[i], ids[i], roles[i])
                graph.add_node(node)
                node_map[ids[i]] = node

            connected = set()
            available = set(ids)
            current = ids[0]
            connected.add(current)
            available.remove(current)

            # Asegurar conectividad mínima
            while available:
                next_node = available.pop()
                origin = node_map[current]
                destination = node_map[next_node]
                weight = random.randint(5, 25)
                graph.add_edge(Edge(origin, destination, weight))
                connected.add(next_node)
                current = next_node

            # Agregar aristas adicionales
            while len(graph.edges) < n_edges:
                u, v = random.sample(ids, 2)
                if u != v:
                    origin = node_map[u]
                    destination = node_map[v]
                    weight = random.randint(5, 25)
                    graph.add_edge(Edge(origin, destination, weight))

            return graph
        
        # Crear y guardar grafo en session_state
        st.session_state.graph = generate_graph(number_of_nodes, number_of_edges)
        

        
    if st.session_state.get("sim_started", False):
        st.info("🔄 Simulación en curso... Espere a que se completen los cálculos.")

import streamlit as st
import random
import string
import sys
import os

# Agrega el directorio raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.graph import Node, Graph
from model.edge import Edge
from networkx_adapter import NetworkXAdapter
from collections import deque
from avl_visualizer import AVLVisualizer




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


# ===== funcion auxiliar =====

def bfs_with_battery(graph, origin_id, destination_id, battery_limit=50):
    visited = set()
    queue = deque()
    # Cada elemento es (nodo_actual, ruta_hasta_ahora, costo_actual)
    queue.append((origin_id, [origin_id], 0))

    while queue:
        current_id, path, cost = queue.popleft()

        if current_id == destination_id and cost <= battery_limit:
            return path, cost

        if (current_id, cost) in visited:
            continue
        visited.add((current_id, cost))

        for edge in graph.get_edges():
            if edge.origin.id == current_id:
                neighbor = edge.destination
                new_cost = cost + edge.weight

                # Si se supera la batería, sólo se continúa si el nodo es de recarga
                if new_cost <= battery_limit:
                    queue.append((neighbor.id, path + [neighbor.id], new_cost))
                elif neighbor.type == "recarga":
                    queue.append((neighbor.id, path + [neighbor.id], edge.weight))  # recarga resetea batería
            elif edge.destination.id == current_id:
                neighbor = edge.origin
                new_cost = cost + edge.weight
                if new_cost <= battery_limit:
                    queue.append((neighbor.id, path + [neighbor.id], new_cost))
                elif neighbor.type == "recarga":
                    queue.append((neighbor.id, path + [neighbor.id], edge.weight))  # resetea batería

    return None, None  # No se encontró ruta válida

with tabs[1]:
    st.subheader("📡 Red de Nodos")

    if st.session_state.get("sim_started") and "graph" in st.session_state:
        
        graph = st.session_state.graph
        adapter = NetworkXAdapter(graph)

        # Dibujar una red
        fig = adapter.draw_network()
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("✈ Buscar Ruta")

        node_ids = [node.id for node in graph.get_vertices()]
        origin_id = st.selectbox("🌍 Nodo Origen", node_ids)
        destination_id = st.selectbox("🎯 Nodo Destino", node_ids)

        if st.button("🔍 Calcular Ruta"):
            path, cost = bfs_with_battery(graph, origin_id, destination_id, battery_limit=50)

            if path:
                st.success(f"✅ Ruta encontrada: {' → '.join(path)} | Costo total: {cost}")
               
                # Vuelve a dibujar la red con la ruta en rojo
                st.pyplot(adapter.draw_network(route=path))

                if st.button("✅ Complete Delivery and Create Order"):
                    st.success("📦 Pedido registrado correctamente.")
            else:
                st.error("❌ No se encontró una ruta válida dentro del límite de batería, ni usando recarga.")
    else:
        st.warning("⚠️ Inicia primero una simulación para visualizar la red.")


with tabs[2]:
    st.subheader("📋 Pedidos y Clientes")
    st.warning("📦 Visualización de pedidos en desarrollo.")


with tabs[3]:
    st.subheader("🚦 Analisis de Rutas")
    st.warning("🚦 Análisis de rutas en desarrollo.")

    if st.session_state.get("sim_started"):

        class DummyAVLNode:
            def __init__(self, key, route, frequency):
                self.key = key
                self.route = route
                self.frequency = frequency
                self.left = None
                self.right = None

        class DummyAVLTree:
            def __init__(self):
                self.root = DummyAVLNode("A-B-C", ["A", "B", "C"], 5)

        dummy_avl = DummyAVLTree()
        visualizer = AVLVisualizer(dummy_avl)
        st.pyplot(visualizer.draw())
    
    else:
        st.warning("⚠️ Inicia primero una simulación para visualizar las rutas más frecuentes.")



       

    



    
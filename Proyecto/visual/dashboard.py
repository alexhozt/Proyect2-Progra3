# Importación de librerías necesarias
import streamlit as st  # Para la interfaz web
import random  # Para generación aleatoria
import sys  # Para manipulación del sistema
import os  # Para operaciones con el sistema de archivos
import matplotlib.pyplot as plt  # Para visualización de gráficos

# Configuración de rutas para importar módulos personalizados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importación de clases personalizadas
from model.graph import Node, Graph  # Modelos de grafo y nodos
from model.edge import Edge  # Modelo de arista
from networkx_adapter import NetworkXAdapter  # Adaptador para visualización de grafos
from collections import deque  # Estructura de datos para BFS
from avl_visualizer import AVLTree, AVLVisualizer  # Para árbol AVL y su visualización
from domain.client import ClientManager  # Gestor de clientes
from domain.order import OrderManager, Order  # Gestor de pedidos
from auxilar_func.statics import Statics  # Funciones estadísticas

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="Sistema de Simulación de Drones",
    layout="wide",
    page_icon="🚁"
)

# ===== ESTILOS CSS PERSONALIZADOS =====
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

# ===== ENCABEZADO DE LA PÁGINA =====
st.markdown("<h1 style='text-align: center;'>🚁 Sistema de Simulación de Drones</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #888;'>Correos Chile - Plataforma de Simulación</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

# ===== TARJETAS DE MÉTRICAS =====
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

# ===== PESTAÑAS PRINCIPALES =====
tabs = st.tabs(["🎮 Simulación", "📡 Red de Nodos", "📋 Pedidos", "🚦 Rutas", "📈 Estadísticas"])

# ===== FUNCIÓN PARA GENERAR IDs ÚNICOS =====
def generate_unique_ids(n):
    """Genera IDs al estilo Excel (A, B, ..., Z, AA, AB, etc.)"""
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

# ===== FUNCIÓN PARA GENERAR GRAFO =====
def generate_graph(n_nodes, n_edges, client_ratio=0.6, storage_ratio=0.2):
    """
    Genera un grafo aleatorio con:
    - n_nodes: número total de nodos
    - n_edges: número total de aristas
    - client_ratio: proporción de nodos clientes
    - storage_ratio: proporción de nodos almacenamiento
    """
    graph = Graph()
    
    # Distribución de tipos de nodos
    roles = (
        ['cliente'] * int(n_nodes * client_ratio) +
        ['almacenamiento'] * int(n_nodes * storage_ratio) +
        ['recarga'] * (n_nodes - int(n_nodes * client_ratio) - int(n_nodes * storage_ratio))
    )
    random.shuffle(roles)

    # Creación de nodos con IDs únicos
    ids = generate_unique_ids(n_nodes)
    node_map = {}

    for i in range(n_nodes):
        node = Node(ids[i], ids[i], roles[i])
        graph.add_node(node)
        node_map[ids[i]] = node

    # Algoritmo para garantizar conectividad mínima
    connected = set()
    available = set(ids)
    current = ids[0]
    connected.add(current)
    available.remove(current)

    while available:
        next_node = available.pop()
        origin = node_map[current]
        destination = node_map[next_node]
        weight = random.randint(5, 25)
        graph.add_edge(Edge(origin, destination, weight))
        connected.add(next_node)
        current = next_node

    # Añadir aristas adicionales hasta alcanzar el número deseado
    while len(graph.edges) < n_edges:
        u, v = random.sample(ids, 2)
        if u != v:
            origin = node_map[u]
            destination = node_map[v]
            weight = random.randint(5, 25)
            graph.add_edge(Edge(origin, destination, weight))

    return graph

# ===== ALGORITMO BFS CON LIMITACIÓN DE BATERÍA =====
def bfs_with_battery(graph, origin_id, destination_id, battery_limit=50):
    """
    Búsqueda de ruta considerando:
    - Límite de batería
    - Nodos de recarga que reinician el contador
    """
    visited = set()
    queue = deque()
    queue.append((origin_id, [origin_id], 0))  # (nodo_actual, ruta, costo)

    while queue:
        current_id, path, cost = queue.popleft()

        # Si llegamos al destino con batería suficiente
        if current_id == destination_id and cost <= battery_limit:
            return path, cost

        if (current_id, cost) in visited:
            continue
        visited.add((current_id, cost))

        # Explorar vecinos
        for edge in graph.get_edges():
            if edge.origin.id == current_id:
                neighbor = edge.destination
                new_cost = cost + edge.weight

                # Manejo de batería y nodos de recarga
                if new_cost <= battery_limit:
                    queue.append((neighbor.id, path + [neighbor.id], new_cost))
                elif neighbor.type == "recarga":
                    # Reiniciamos contador al pasar por recarga
                    queue.append((neighbor.id, path + [neighbor.id], edge.weight))  

    return None, None  # No se encontró ruta válida

# ===== FUNCIÓN PARA REGISTRAR ENTREGA =====
def registrar_entrega():
    """Registra una entrega completada y crea el pedido correspondiente"""
    path = st.session_state.current_path
    route_key = " → ".join(path)

    # Inicializar árbol AVL si no existe
    if "route_avl" not in st.session_state:
        st.session_state.route_avl = AVLTree()
    st.session_state.route_avl.insert(route_key)

    # Inicializar contador de visitas si no existe
    if "visitas_por_nodo" not in st.session_state:
        st.session_state.visitas_por_nodo = {}

    # Actualizar contadores de visitas
    for nodo_id in path:
        st.session_state.visitas_por_nodo[nodo_id] = st.session_state.visitas_por_nodo.get(nodo_id, 0) + 1

    # Crear nuevo pedido entregado
    order_manager = st.session_state.order_manager
    client_manager = st.session_state.client_manager
    destination_id = path[-1]
    client = client_manager.get_client_by_node_id(destination_id)

    if client:
        from datetime import datetime
        import uuid

        nueva_orden = Order(
            order_id=str(uuid.uuid4()),
            client=client.name,
            client_id=client.client_id,
            node_id=destination_id,
            origin=path[0],
            destination=destination_id,
            status="delivered",
            priority=0,
            created_at=datetime.now().isoformat(),
            delivered_at=datetime.now().isoformat(),
            route_cost=st.session_state.current_cost
        )

        order_manager.orders.append(nueva_orden)
        client_manager.increment_order_count(destination_id)

        st.success("📦 Pedido registrado correctamente.")
        st.rerun()
    else:
        st.warning("⚠️ No se pudo registrar el pedido: el nodo destino no está asociado a un cliente.")

# ===== PESTAÑA 1: SIMULACIÓN =====
with tabs[0]:
    st.subheader("🎮 Parámetros de la Simulación")

    # Controles para parámetros de simulación
    col1, col2, col3 = st.columns(3)
    with col1:
        number_of_nodes = st.slider("🔢 Nodos totales", 10, 150, 30)
    with col2:
        number_of_edges = st.slider("🔗 Conexiones (aristas)", 10, 300, 60)
    with col3:
        number_of_orders = st.slider("📦 Pedidos", 1, 500, 25)

    # Cálculo de distribución de nodos
    client_nodes = int(0.6 * number_of_nodes)
    storage_nodes = int(0.2 * number_of_nodes)
    recharge_nodes = number_of_nodes - client_nodes - storage_nodes

    st.markdown("---")
    st.markdown("### 🧠 Distribución Calculada:")
    st.markdown(f"- 👤 Clientes: **{client_nodes}**")
    st.markdown(f"- 📦 Almacenamiento: **{storage_nodes}**")
    st.markdown(f"- 🔋 Recarga: **{recharge_nodes}**")

    # Botón para iniciar simulación
    if st.button("🚀 Ejecutar Simulación"):
        st.success("✅ Simulación iniciada correctamente.")
        st.session_state.sim_started = True
        
        # Generar y almacenar grafo
        st.session_state.graph = generate_graph(number_of_nodes, number_of_edges)
        
        # Obtener nodos clientes
        all_nodes = st.session_state.graph.get_vertices()
        client_nodes = [n for n in all_nodes if n.type == 'cliente']
        
        # Generar clientes y pedidos
        st.session_state.client_manager = ClientManager()
        st.session_state.client_manager.generate_clients(client_nodes)
        
        st.session_state.order_manager = OrderManager(st.session_state.client_manager)
        st.session_state.order_manager.generate_initial_orders(
            number_of_orders,
            client_nodes,
            all_nodes
        )
              
    if st.session_state.get("sim_started", False):
        st.info("🔄 Simulación en curso... Espere a que se completen los cálculos.")

# ===== PESTAÑA 2: RED DE NODOS =====
with tabs[1]:
    st.subheader("📡 Red de Nodos")

    if st.session_state.get("sim_started") and "graph" in st.session_state:
        # Visualización del grafo
        graph = st.session_state.graph
        adapter = NetworkXAdapter(graph)
        fig = adapter.draw_network()
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("✈ Buscar Ruta")

        # Selectores de origen y destino
        node_ids = [node.id for node in graph.get_vertices()]
        origin_id = st.selectbox("🌍 Nodo Origen", node_ids)
        destination_id = st.selectbox("🎯 Nodo Destino", node_ids)

        # Botón para calcular ruta
        if st.button("🔍 Calcular Ruta"):
            path, cost = bfs_with_battery(graph, origin_id, destination_id, battery_limit=50)

            if path:
                # Almacenar ruta encontrada
                st.session_state.current_path = path
                st.session_state.current_cost = cost
                st.success(f"✅ Ruta encontrada: {' → '.join(path)} | Costo total: {cost}")
                # Visualizar grafo con ruta resaltada
                st.pyplot(adapter.draw_network(route=path))
            else:
                st.error("❌ No se encontró una ruta válida dentro del límite de batería, ni usando recarga.")

        # Botón para registrar entrega (sólo si hay ruta)
        if "current_path" in st.session_state:
            if st.button("✅ Complete Delivery and Create Order"):
                registrar_entrega()
                st.success("📦 Pedido registrado correctamente.")
            
    else:
        st.warning("⚠️ Inicia primero una simulación para visualizar la red.")

# ===== PESTAÑA 3: PEDIDOS =====
with tabs[2]:
    st.subheader("📋 Pedidos y Clientes")
    
    if st.session_state.get("sim_started"):
        tab1, tab2 = st.tabs(["👤 Clientes", "📦 Pedidos"])
        
        with tab1:
            st.markdown("### 👤 Lista de Clientes")
            if "client_manager" in st.session_state:
                # Mostrar clientes ordenados
                clients = sorted(
                    st.session_state.client_manager.clients,
                    key=lambda x: x.client_id
                )
                st.json([c.to_dict() for c in clients])
            else:
                st.warning("No se han generado clientes aún.")
        
        with tab2:
            st.markdown("### 📦 Pedidos")
            if "order_manager" in st.session_state:
                # Mostrar pedidos ordenados por estado y prioridad
                orders = sorted(
                    st.session_state.order_manager.orders,
                    key=lambda x: (x.status != 'pending', -x.priority)
                )
                st.json([o.to_dict() for o in orders])
                
                # Mostrar métricas de pedidos
                pending = len([o for o in orders if o.status == "pending"])
                delivered = len([o for o in orders if o.status == "delivered"])
                st.metric("Pedidos pendientes", pending - delivered)
                st.metric("Pedidos entregados", delivered)
            else:
                st.warning("No se han generado pedidos aún.")
    else:
        st.warning("⚠️ Ejecuta primero una simulación para ver los clientes y pedidos.")

# ===== PESTAÑA 4: RUTAS =====
with tabs[3]:
    st.subheader("🚦 Analisis de Rutas")
    
    if "route_avl" not in st.session_state:
        st.warning("⚠️ No hay rutas registradas. Completa entregas primero en la pestaña de Rutas.")
    else:
        avl_tree = st.session_state.route_avl

        # Mostrar rutas ordenadas
        st.markdown("### 📋 Rutas más frecuentes (ordenadas por nombre):")
        routes = avl_tree.inorder()
        if routes:
            for key, freq in routes:
                st.markdown(f"- **Ruta:** {key} | **Frecuencia:** {freq}")
        else:
            st.warning("⚠️ No hay rutas registradas.")

        st.markdown("---")

        # Visualizar árbol AVL
        st.subheader("📊 Visualización del Árbol AVL de Rutas")
        visualizer = AVLVisualizer()
        fig = visualizer.draw(avl_tree.root)
        st.pyplot(fig)

# ===== PESTAÑA 5: ESTADÍSTICAS =====
with tabs[4]:
    st.subheader("📈 Estadísticas")

    if st.session_state.get("sim_started") and "graph" in st.session_state:
        grafo = st.session_state.graph
        nodos = grafo.get_vertices()
        visitas = st.session_state.get("visitas_por_nodo", {})

        # Gráfico de distribución de tipos de nodo
        st.markdown("### 🥧 Distribución de nodos por tipo")
        roles = {"cliente": 0, "almacenamiento": 0, "recarga": 0}
        for nodo in nodos:
            roles[nodo.type] += 1
        st.pyplot(Statics.pie_chart(roles))

        # Gráfico de visitas por tipo de nodo
        st.markdown("### 📊 Visitas a nodos por tipo")
        tipo_visitas = {"cliente": 0, "almacenamiento": 0, "recarga": 0}
        for nodo in nodos:
            visitas_nodo = visitas.get(nodo.id, 0)
            tipo_visitas[nodo.type] += visitas_nodo
        st.pyplot(Statics.bar_chart(tipo_visitas))

        # Top nodos más visitados por tipo
        st.markdown("### ⭐ Top nodos más visitados por tipo")
        
        fig_cliente = Statics.bar_chart_top_nodos(nodos, visitas, "cliente")
        fig_recarga = Statics.bar_chart_top_nodos(nodos, visitas, "recarga")
        fig_almacen = Statics.bar_chart_top_nodos(nodos, visitas, "almacenamiento")

        if fig_cliente:
            st.pyplot(fig_cliente)
        else:
            st.info("🔵 No hay visitas registradas a nodos de tipo 'cliente'.")

        if fig_recarga:
            st.pyplot(fig_recarga)
        else:
            st.info("🟢 No hay visitas registradas a nodos de tipo 'recarga'.")

        if fig_almacen:
            st.pyplot(fig_almacen)
        else:
            st.info("🟠 No hay visitas registradas a nodos de tipo 'almacenamiento'.")

    else:
        st.warning("⚠️ Ejecuta primero una simulación para ver estadísticas.")
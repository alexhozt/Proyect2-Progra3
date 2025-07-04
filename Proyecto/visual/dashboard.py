# Para Inciarl Streamlit usa python -m streamlit run visual/dashboard.py

#HAY UNOS WARNINGS DE MATPLOTLIB ES QUE CUANODO SE GENERAN LOS NODOS SE CREAN CON UNOS EMOJIS QUE NO SON CAPACES DE PROCESAR HAY
#QUE QUITARLOS ESO Xd

import streamlit as st
from visual.network_adapter import NetworkXAdapter
from simulacion.init_simulation import generar_red
from simulacion.simulation import Simulation
from visual.avl_visualizer import AVLVisualizer
import random
import pandas as pd
from collections import deque
import plotly.express as px
import math
from streamlit_folium import folium_static
from visual.MAP.map_visualizer import generar_mapa  
import networkx as nx 
from visual.generator_report import generar_pdf


def calcular_mst(graph):
    import networkx as nx  # por si está afuera

    G = nx.Graph()
    
    for v in graph.vertices():
        G.add_node(str(v))
    
    for e in graph.edges():
        u, v = e.endpoints()
        peso = e.element()
        G.add_edge(str(u), str(v), weight=peso)

    mst = nx.minimum_spanning_tree(G, algorithm="kruskal")
    mst_edges = [(u, v, mst[u][v]["weight"]) for u, v in mst.edges()]
    return mst_edges


def calcular_ruta_optima(graph, origen, destino, algoritmo="Dijkstra", max_autonomia=50):
    import networkx as nx
    G = nx.DiGraph()

    for v in graph.vertices():
        G.add_node(str(v))

    for e in graph.edges():
        u, v = e.endpoints()
        G.add_edge(str(u), str(v), weight=e.element())

    def calcular_camino(source, target):
        try:
            if algoritmo == "Dijkstra":
                path = nx.dijkstra_path(G, str(source), str(target), weight="weight")
                cost = nx.dijkstra_path_length(G, str(source), str(target), weight="weight")
            elif algoritmo == "Floyd-Warshall":
                pred, dist = nx.floyd_warshall_predecessor_and_distance(G, weight="weight")
                path = []
                current = str(target)
                while current != str(source):
                    path.insert(0, current)
                    current = pred[str(source)][current]
                path.insert(0, str(source))
                cost = dist[str(source)][str(target)]
            else:
                return None, None
            return path, cost
        except:
            return None, None

    # Intentar ruta directa
    path, cost = calcular_camino(origen, destino)
    if path and cost <= max_autonomia:
        return path, cost

    # Si supera autonomía, buscar vía recarga
    recargas = [v for v in graph.vertices() if str(v).startswith("🔋")]
    for nodo_recarga in recargas:
        tramo1, cost1 = calcular_camino(origen, nodo_recarga)
        tramo2, cost2 = calcular_camino(nodo_recarga, destino)
        if tramo1 and tramo2 and cost1 <= max_autonomia and cost2 <= max_autonomia:
            nueva_ruta = tramo1[:-1] + tramo2  # evitar repetir nodo recarga
            nuevo_costo = cost1 + cost2
            return nueva_ruta, nuevo_costo

    # No se encontró ruta válida
    return None, None



# Configuración de la interfaz
st.set_page_config(page_title="Sistema de Drones", layout="wide")

if "mostrar_mst" not in st.session_state:
    st.session_state["mostrar_mst"] = False


# Sidebar de navegación (5 pestañas)
tabs = st.tabs(["🔄 Run Simulation", "🌍 Explore Network", "🌐 Clients & Orders", "📋 Route Analytics", "📈 General Statistics"])

# ============================
# 🔄 PESTAÑA 1: Run Simulation
# ============================

with tabs[0]:
    st.header("🔄 Simulación de Red de Drones")

    st.markdown("Configura los parámetros para iniciar la simulación:")

    n_nodes = st.slider("Número de nodos", min_value=10, max_value=150, value=15)
    m_edges = st.slider("Número de aristas", min_value=n_nodes - 1, max_value=min(300, n_nodes*(n_nodes - 1)//2), value=20)
    n_orders = st.slider("Número de órdenes", min_value=10, max_value=300, value=10)

    n_almacen = int(n_nodes * 0.20)
    n_recarga = int(n_nodes * 0.20)
    n_clientes = n_nodes - n_almacen - n_recarga

    st.markdown("""
    **Distribución de nodos:**  
    📦 Almacenamiento: {} (20%)  
    🔋 Recarga: {} (20%)  
    👤 Clientes: {} (60%)
    """.format(n_almacen, n_recarga, n_clientes))

    if st.button("📊 Start Simulation"):
        graph, sim = generar_red(n_nodes, m_edges, n_almacen, n_recarga, n_clientes)
        st.session_state["graph"] = graph
        st.session_state["sim"] = sim


        # Registrar clientes automáticamente
        for i in range(n_clientes):
            client_id = f"C{i:03}"
            name = f"Cliente {i}"
            client_type = random.choice(["premium", "normal"])
            sim.register_client(client_id, name, client_type)

        # Función para encontrar rutas válidas con BFS
        def bfs(graph, start, end):
            visited = set()
            queue = deque([(start, [start], 0)])

            while queue:
                current, path, cost = queue.popleft()
                if current == end:
                    return path, cost
                for neighbor in graph.neighbors(current):
                    if neighbor not in path:
                        edge = graph.get_edge(current, neighbor)
                        queue.append((neighbor, path + [neighbor], cost + edge.element()))
            return None, None

        vertices = list(graph.vertices())
        client_nodes = [v for v in graph.vertices() if str(v).startswith("👤")]
        if len(client_nodes) >= 2:
            for i in range(n_orders):
                origin = random.choice(client_nodes)
                destination = random.choice([v for v in client_nodes if v != origin])
                path, cost = bfs(graph, origin, destination)
                if path:
                    sim.create_order(f"C{i:03}", origin, destination, priority=1, path=path, cost=cost)

        st.session_state["graph"] = graph
        st.session_state["sim"] = sim
        st.session_state["simulation_started"] = True
        st.session_state["adapter"] = NetworkXAdapter(graph)

        st.success("Simulación iniciada correctamente 🚀")

# =============================
# 🌍 PESTAÑA 2: Explore Network
# =============================
with tabs[1]:
    st.header("🌍 Explora la Red de Drones")

    if st.session_state.get("simulation_started"):
        graph = st.session_state["graph"]
        sim = st.session_state["sim"]

        st.subheader("🗺️ Visualización en Mapa Real")

        # Solo generar nodos/aristas una vez
        if "nodos" not in st.session_state or "aristas" not in st.session_state:
            nodos = []
            aristas = []
            for v in graph.vertices():
                label = str(v)
                tipo = label[0]
                lat = -38.735 + random.uniform(-0.01, 0.01)
                lon = -72.590 + random.uniform(-0.01, 0.01)
                nodos.append((label, lat, lon, tipo))

            for e in graph.edges():
                u, v = e.endpoints()
                aristas.append((str(u), str(v), e.element()))

            st.session_state["nodos"] = nodos
            st.session_state["aristas"] = aristas

        ruta = st.session_state.get("ruta")
        mst_resultado = st.session_state.get("mst_resultado")

        st.subheader("✈ Calcular Ruta entre Nodos")

        origenes = [v for v in graph.vertices() if str(v).startswith("📦")]
        destinos = [v for v in graph.vertices() if str(v).startswith("👤")]

        origen = st.selectbox("📦 Nodo de Origen (Almacenamiento)", origenes, format_func=str)
        destino = st.selectbox("👤 Nodo de Destino (Cliente)", destinos, format_func=str)

        algoritmo = st.radio("⚙️ Algoritmo de Ruta", ["Dijkstra", "Floyd-Warshall"])

        if st.button("✈ Calcular Ruta"):
            path, cost = calcular_ruta_optima(graph, origen, destino, algoritmo)
            if path:
                st.session_state["ruta"] = path
                st.session_state["ruta_costo"] = cost
                ruta = path
                st.success(f"Ruta con {algoritmo}: {' → '.join(ruta)} | Costo total: {cost}")

                recarga_en_ruta = any("🔋" in n for n in ruta)
                tiempo_estimado = round(cost * 1.2, 2)

                with st.expander("📝 Resumen de vuelo"):
                    st.markdown(f"**Nodos visitados:** {len(ruta)}")
                    st.markdown(f"**Ruta completa:** {' → '.join(ruta)}")
                    st.markdown(f"**Distancia total:** {cost} unidades")
                    st.markdown(f"**Tiempo estimado de vuelo:** {tiempo_estimado} minutos")
                    st.markdown(f"**Recarga necesaria:** {'✅ Sí' if recarga_en_ruta else '❌ No'}")
            else:
                st.error("No se encontró una ruta válida entre esos nodos.")

        st.subheader("🌲 Árbol de Expansión Mínima (Kruskal)")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌲 Mostrar MST"):
                mst_resultado = calcular_mst(graph)
                st.session_state["mst_resultado"] = mst_resultado
                st.success(f"MST calculado con {len(mst_resultado)} conexiones.")
        with col2:
            if st.button("❌ Ocultar MST"):
                st.session_state["mst_resultado"] = None
                mst_resultado = None

        # Mostrar mapa final con ruta y/o MST persistente
        mapa = generar_mapa(
            st.session_state["nodos"],
            st.session_state["aristas"],
            ruta=st.session_state.get("ruta"),
            mst=st.session_state.get("mst_resultado")
        )
        if mapa:
            folium_static(mapa)
        else:
            st.error("No se pudo generar el mapa.")

    else:
        st.info("Primero inicia una simulación en la pestaña anterior.")
                


        

# ==========================
# 🌐 PESTAÑA 3: Clients & Orders
# ==========================

with tabs[2]:
    st.header("🌐 Clients and Orders")

    if st.session_state.get("simulation_started"):
        sim = st.session_state["sim"]

        st.subheader("👤 Clients")
        clients = sim.get_clients()
        if clients:
            for client in clients:
                if "type" not in client:
                    client["type"] = random.choice(["premium", "normal"])
            st.dataframe(pd.DataFrame(clients))
        else:
            st.info("No hay clientes registrados todavía.")

        st.subheader("📦 Orders")
        orders = sim.get_orders()
        if orders:
            # Ajustar visualización del campo delivered_at
            for order in orders:
                if order["delivered_at"] in [None, "null", "", "None"]:
                    order["delivered_at"] = "Aún no se completó el envío"
            st.dataframe(pd.DataFrame(orders))
        else:
            st.info("No hay órdenes registradas todavía.")
    else:
        st.info("Inicia una simulación para ver clientes y órdenes.")


# =============================
# 📋 PESTAÑA 4: Route Analytics
# =============================

with tabs[3]:
    st.header("📋 Rutas frecuentes")

    if "sim" in st.session_state:
        sim = st.session_state["sim"]
        rutas = sim.get_frequent_routes()

        if rutas:
            rutas.sort()  # Ordenar por recorrido (orden lexicográfico)

            st.subheader("📋 Rutas más frecuentes")
            for i, (ruta, freq) in enumerate(rutas, start=1):
                st.markdown(f"{i}. Route hash: {ruta} | Frequency: {freq}")

            st.subheader("📊 AVL Tree Visualization")
            from visual.avl_visualizer import AVLVisualizer
            visualizer = AVLVisualizer(sim.routes_avl)
            visualizer.draw(use_hierarchy=True)

            st.subheader("📄 Generar Informe PDF")

            if st.button("📄 Generar Informe"):
                orders = sim.get_orders()
                clients = sim.get_clients()
                rutas_frecuentes = sim.get_frequent_routes()

                from generator_report import generar_pdf, guardar_graficos_pdf
                graph = st.session_state["graph"]
                
                guardar_graficos_pdf(graph, sim)  # 💾 genera los .png antes del PDF

                ruta_pdf = generar_pdf(orders, clients, rutas_frecuentes)
                with open(ruta_pdf, "rb") as file:
                    st.download_button("⬇️ Descargar Informe PDF", file, file_name="informe_drones.pdf")


        else:
            st.warning("No hay rutas registradas aún.")
    else:
        st.info("Inicia una simulación para analizar rutas.")



# ==============================
# 📈 PESTAÑA 5: General Statistics
# ==============================



with tabs[4]:
    st.header("📈 General Statistics")
    st.write("DEBUG - graph:", "OK" if "graph" in st.session_state else "MISSING")
    st.write("DEBUG - sim:", "OK" if "sim" in st.session_state else "MISSING")

    graph = st.session_state.get("graph")
    sim = st.session_state.get("sim")

    if graph and sim:
        roles = {"📦": "Storage", "🔋": "Recharge", "👤": "Client"}
        role_counts = {"📦": 0, "🔋": 0, "👤": 0}
        visit_counts = {"📦": {}, "🔋": {}, "👤": {}}

        for v in graph.vertices():
            name = str(v)
            for symbol in roles:
                if name.startswith(symbol):
                    role_counts[symbol] += 1
                    visit_counts[symbol][name] = 0

        # Simulación: contar visitas reales por nodo en las rutas
        for order in sim.get_orders():
            for node in order.get("path", []):
                node_str = str(node)
                for symbol in visit_counts:
                    if node_str in visit_counts[symbol]:
                        visit_counts[symbol][node_str] += 1

        labels = [roles[k] for k in role_counts]
        sizes = [int(role_counts[k]) if role_counts[k] and not math.isnan(role_counts[k]) else 0 for k in role_counts]

        if sum(sizes) > 0:
            st.subheader("📊 Top Visited Nodes by Role")

            col1, col2, col3 = st.columns(3)
            cols = {"👤": col1, "🔋": col2, "📦": col3}

            for symbol in ["👤", "🔋", "📦"]:
                sorted_visits = sorted(visit_counts[symbol].items(), key=lambda x: x[1], reverse=True)[:5]
                if sorted_visits:
                    df_bar = pd.DataFrame(sorted_visits, columns=["Nodo", "Visitas"])
                    fig = px.bar(
                        df_bar,
                        x="Nodo",
                        y="Visitas",
                        title=f"Most Visited {roles[symbol]} Nodes",
                        text_auto=True
                    )
                    fig.update_traces(marker_color="#1E65C9", hovertemplate="Nodo: %{x}<br>Visitas: %{y}")
                    with cols[symbol]:
                        st.plotly_chart(fig, use_container_width=True)

            # 🥧 Gráfico de torta - proporción de roles
            st.subheader("🥧 Pie Chart: Node Role Distribution")
            df_pie = pd.DataFrame({
                "Rol": labels,
                "Cantidad": sizes
            })
            fig_pie = px.pie(df_pie, values="Cantidad", names="Rol", title="Distribución de Roles", hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("No hay nodos registrados para mostrar estadísticas.")
    else:
        st.warning("No se encontró un grafo generado o simulación activa.")
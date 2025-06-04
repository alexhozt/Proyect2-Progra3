# visual/network_adapter.py

import networkx as nx
import matplotlib.pyplot as plt

class NetworkXAdapter:
    def __init__(self, graph):
        """
        :param graph: Instancia del grafo propio del sistema (no de networkx)
        """
        self.graph = graph  # grafo personalizado con nodos y aristas
        self.nx_graph = nx.Graph()

    def build_networkx_graph(self):
        self.nx_graph.clear()

        for node in self.graph.get_vertices():
            self.nx_graph.add_node(
                node.id,
                label=node.label,
                type=node.type
            )

        for edge in self.graph.get_edges():
            self.nx_graph.add_edge(
                edge.origin.id,
                edge.destination.id,
                weight=edge.weight
            )

    def draw_network(self, route=None):
        """
        Dibuja el grafo completo. Si se entrega una ruta, se marca en rojo.
        :param route: lista de IDs de nodos (ej. ['A', 'B', 'C'])
        """
        self.build_networkx_graph()

        pos = nx.spring_layout(self.nx_graph, seed=42)

        # Colores según tipo de nodo
        color_map = {
            "almacenamiento": "#3498db",
            "recarga": "#2ecc71",
            "cliente": "#e74c3c"
        }

        node_colors = [
            color_map.get(self.nx_graph.nodes[n]["type"], "#95a5a6")
            for n in self.nx_graph.nodes
        ]

        edge_colors = []
        for u, v in self.nx_graph.edges:
            if route and self._is_edge_in_route(u, v, route):
                edge_colors.append("red")
            else:
                edge_colors.append("gray")

        labels = nx.get_node_attributes(self.nx_graph, "label")

        nx.draw(
            self.nx_graph,
            pos,
            with_labels=True,
            labels=labels,
            node_color=node_colors,
            edge_color=edge_colors,
            node_size=800,
            font_size=10
        )
        plt.title("Red de nodos del sistema")
        fig = plt.gcf()  # get current figure
        return fig


    def _is_edge_in_route(self, u, v, route):
        """
        Verifica si un borde pertenece a una ruta específica
        """
        for i in range(len(route) - 1):
            if (route[i] == u and route[i+1] == v) or (route[i] == v and route[i+1] == u):
                return True
        return False

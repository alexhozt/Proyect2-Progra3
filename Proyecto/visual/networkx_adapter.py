import networkx as nx
import matplotlib.pyplot as plt

class NetworkXAdapter:
    """
    Adaptador que convierte nuestro grafo personalizado a un grafo de NetworkX para visualización.
    Proporciona métodos para construir y dibujar el grafo con opciones de personalización.
    """
    
    def __init__(self, graph):
        """
        Constructor que inicializa el adaptador con nuestro grafo personalizado.
        
        Args:
            graph (Graph): Instancia de nuestro grafo personalizado (modelo propio)
        """
        self.graph = graph  # Guarda referencia al grafo original del sistema
        self.nx_graph = nx.Graph()  # Crea un grafo NetworkX vacío para la visualización

    def build_networkx_graph(self):
        """
        Construye el grafo de NetworkX a partir de nuestro grafo personalizado.
        Convierte nodos y aristas preservando todos los atributos.
        """
        self.nx_graph.clear()  # Limpia el grafo anterior (si existía)

        # Agrega todos los nodos del grafo original
        for node in self.graph.get_vertices():
            self.nx_graph.add_node(
                node.id,  # Identificador único del nodo
                label=node.label,  # Etiqueta para mostrar
                type=node.type  # Tipo: 'cliente', 'almacenamiento' o 'recarga'
            )

        # Agrega todas las aristas del grafo original
        for edge in self.graph.get_edges():
            self.nx_graph.add_edge(
                edge.origin.id,  # Nodo origen
                edge.destination.id,  # Nodo destino
                weight=edge.weight  # Peso de la arista
            )

    def draw_network(self, route=None):
        """
        Genera una visualización del grafo usando matplotlib.
        
        Args:
            route (list, optional): Lista de IDs de nodos que forman una ruta a resaltar.
                                   Ejemplo: ['A', 'B', 'C']
        
        Returns:
            matplotlib.figure.Figure: Figura con el grafo dibujado
        """
        self.build_networkx_graph()  # Reconstruye el grafo NetworkX

        # Calcula posiciones de los nodos usando un layout spring (fuerzas)
        pos = nx.spring_layout(self.nx_graph, seed=42)  # seed para consistencia

        # Mapeo de colores según el tipo de nodo
        color_map = {
            "almacenamiento": "#3498db",  # Azul para almacenes
            "recarga": "#2ecc71",  # Verde para recargas
            "cliente": "#e74c3c"  # Rojo para clientes
        }

        # Lista de colores para cada nodo según su tipo
        node_colors = [
            color_map.get(self.nx_graph.nodes[n]["type"], "#95a5a6")  # Gris por defecto
            for n in self.nx_graph.nodes
        ]

        # Determina colores de las aristas (resalta las de la ruta)
        edge_colors = []
        for u, v in self.nx_graph.edges:
            if route and self._is_edge_in_route(u, v, route):
                edge_colors.append("#000000")  # Negro para aristas en la ruta
            else:
                edge_colors.append("gray")  # Gris para aristas normales

        # Obtiene las etiquetas para mostrar en los nodos
        labels = nx.get_node_attributes(self.nx_graph, "label")

        # Dibuja el grafo con los parámetros configurados
        nx.draw(
            self.nx_graph,
            pos,  # Layout calculado
            with_labels=True,
            labels=labels,
            node_color=node_colors,
            edge_color=edge_colors,
            node_size=500,  # Tamaño de los nodos
            font_size=8,
            font_weight='bold'
        )
        
        plt.title("Red de nodos del sistema")  # Título del gráfico
        fig = plt.gcf()  # Obtiene la figura actual
        return fig  # Retorna la figura para su visualización

    def _is_edge_in_route(self, u, v, route):
        """
        Método auxiliar que verifica si una arista (u,v) forma parte de una ruta.
        
        Args:
            u (str): ID del primer nodo de la arista
            v (str): ID del segundo nodo de la arista
            route (list): Lista de IDs de nodos que forman la ruta
        
        Returns:
            bool: True si la arista está en la ruta, False en caso contrario
        """
        # Verifica todas las conexiones consecutivas en la ruta
        for i in range(len(route) - 1):
            if (route[i] == u and route[i+1] == v) or (route[i] == v and route[i+1] == u):
                return True
        return False
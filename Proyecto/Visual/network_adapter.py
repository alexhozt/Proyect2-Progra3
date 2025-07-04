# Proyecto/Visual/network_adapter.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


class NetworkXAdapter:
    ROLE_PALETTE: Dict[str, str] = {
        "almacen": "#f4d35e",
        "recarga": "#43aa8b",
        "cliente": "#f95738",
    }
    DEFAULT_NODE_COLOR = "#bdbdbd"

    def __init__(self, grafo_personalizado, seed: int = 42):
        self.graph_obj = grafo_personalizado
        self.seed = seed
        self._nxgraph = nx.DiGraph() if grafo_personalizado.is_directed() else nx.Graph()
        self._labels = {}
        self._construir()

    def _extraer_etiqueta(self, nodo) -> str:
        e = nodo.element()
        return getattr(e, "label", str(e))

    def _rol_nodo(self, nodo) -> Optional[str]:
        e = nodo.element()
        return getattr(e, "role", None)

    def _construir(self):
        for nodo in self.graph_obj.vertices():
            etiqueta = self._extraer_etiqueta(nodo)
            rol = self._rol_nodo(nodo)
            self._labels[nodo] = etiqueta
            self._nxgraph.add_node(nodo, label=etiqueta, role=rol)

        for arista in self.graph_obj.edges():
            origen, destino = arista.endpoints()
            peso = arista.element()
            self._nxgraph.add_edge(origen, destino, weight=peso)

    def recargar(self):
        self._nxgraph.clear()
        self._construir()

    def _calcular_posiciones(self) -> Dict[Any, Tuple[float, float]]:
        return nx.spring_layout(self._nxgraph, seed=self.seed)

    def dibujar(
        self,
        ruta_destacada: Optional[Sequence] = None,
        mostrar_pesos: bool = True,
        tamaño_figura: Tuple[int, int] = (10, 6),
        contenedor_st=None,
    ):
        pos = self._calcular_posiciones()

        colores_nodos = [
            self.ROLE_PALETTE.get(self._nxgraph.nodes[n].get("role"), self.DEFAULT_NODE_COLOR)
            for n in self._nxgraph.nodes()
        ]

        pares_resaltados = set()
        if ruta_destacada and len(ruta_destacada) > 1:
            enlaces = zip(ruta_destacada, ruta_destacada[1:])
            pares_resaltados = set(enlaces) | {(v, u) for u, v in enlaces}

        colores_aristas = [
            "#ff595e" if (u, v) in pares_resaltados else "#6c757d"
            for u, v in self._nxgraph.edges()
        ]

        fig, ax = plt.subplots(figsize=tamaño_figura)

        nx.draw(
            self._nxgraph,
            pos,
            ax=ax,
            labels={n: self._labels[n] for n in self._nxgraph.nodes()},
            node_color=colores_nodos,
            edge_color=colores_aristas,
            node_size=950,
            font_size=9,
            width=2,
        )

        if mostrar_pesos:
            etiquetas_aristas = nx.get_edge_attributes(self._nxgraph, "weight")
            nx.draw_networkx_edge_labels(self._nxgraph, pos, edge_labels=etiquetas_aristas, font_size=8)

        self._agregar_leyenda(ax)
        ax.set_title("Red de nodos - Sistema de drones")
        plt.axis("off")

        if contenedor_st:
            contenedor_st.pyplot(fig)
            plt.close()
        elif st:
            st.pyplot(fig)
            plt.close()
        else:
            plt.show()

    def _agregar_leyenda(self, ax):
        parches = [
            mpatches.Patch(color=color, label=nombre.capitalize())
            for nombre, color in self.ROLE_PALETTE.items()
        ]
        ax.legend(handles=parches, loc="lower left")

    @property
    def grafo_nx(self) -> nx.Graph:
        return self._nxgraph

    def ruta_mas_corta(self, inicio, fin) -> List:
        return nx.dijkstra_path(self._nxgraph, source=inicio, target=fin, weight="weight")

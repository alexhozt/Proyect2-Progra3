import streamlit as st
import matplotlib.pyplot as plt


class Statics:

    def pie_chart(data_dict):
        labels = list(data_dict.keys())
        values = list(data_dict.values())
        colors = ['#e74c3c', '#3498db', '#2ecc71']
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.set_title("Proporción de tipos de nodos")
        return fig

    def bar_chart(data_dict):
        labels = list(data_dict.keys())
        values = list(data_dict.values())
        colors = ['#e74c3c', '#2980b9', '#27ae60']
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=colors)
        ax.set_title("Visitas acumuladas a nodos por tipo")
        return fig


    def bar_chart_top_nodos(nodos, visitas, tipo, top_n=3):
        """
        Dibuja un gráfico de barras para los nodos más visitados de un tipo específico.
        """
        nodos_tipo = [n for n in nodos if n.type == tipo]
        visitas_tipo = [(n.id, visitas.get(n.id, 0)) for n in nodos_tipo]
        visitas_tipo.sort(key=lambda x: x[1], reverse=True)
        top_nodos = visitas_tipo[:top_n]

        if not top_nodos:
            return None  # Nada que graficar

        labels = [nid for nid, _ in top_nodos]
        values = [v for _, v in top_nodos]
        fig, ax = plt.subplots()
        colores = {'cliente': '#3498db', 'recarga': '#2ecc71', 'almacenamiento': '#e67e22'}
        ax.bar(labels, values, color=colores.get(tipo, 'gray'))
        ax.set_title(f"{top_n} nodos de tipo '{tipo}' más visitados")
        ax.set_ylabel("Cantidad de visitas")
        return fig
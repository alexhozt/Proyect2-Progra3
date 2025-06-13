import matplotlib.pyplot as plt  # Para crear visualizaciones gráficas
import networkx as nx  # Para manipular y dibujar grafos (usado en AVLVisualizer)

class AVLNode:
    """
    Nodo del árbol AVL que almacena una ruta y su frecuencia de uso.
    Atributos:
        key (str): La ruta almacenada (ej. "A -> B -> C")
        freq (int): Cantidad de veces que se ha usado esta ruta
        left (AVLNode): Hijo izquierdo (rutas menores alfabéticamente)
        right (AVLNode): Hijo derecho (rutas mayores alfabéticamente) 
        height (int): Altura del nodo (para mantener balance del árbol)
    """
    def __init__(self, key):
        self.key = key  # Ruta específica (cadena de texto)
        self.freq = 1  # Contador de frecuencia (inicia en 1)
        self.left = None  # Subárbol izquierdo
        self.right = None  # Subárbol derecho
        self.height = 1  # Altura inicial del nodo

class AVLTree:
    """
    Implementación de un árbol AVL (árbol binario balanceado) para almacenar rutas.
    Mantiene el árbol balanceado automáticamente después de cada inserción.
    """
    def __init__(self):
        """Inicializa un árbol AVL vacío"""
        self.root = None  # Raíz del árbol (inicialmente nula)

    def insert(self, key):
        """
        Inserta una nueva ruta o incrementa su frecuencia si ya existe.
        Args:
            key (str): Ruta a insertar (ej. "A -> B -> C")
        """
        self.root = self._insert(self.root, key)  # Llama al método privado

    def _insert(self, node, key):
        """
        Método recursivo privado para insertar en el árbol.
        Args:
            node (AVLNode): Nodo actual en la recursión
            key (str): Ruta a insertar
        Returns:
            AVLNode: El nodo (posiblemente nuevo) después de la inserción
        """
        # Caso base: llegamos a un nodo nulo, creamos uno nuevo
        if not node:
            return AVLNode(key)

        # Si la ruta ya existe, incrementamos su frecuencia
        if key == node.key:
            node.freq += 1
            return node  # No necesita rebalanceo en este caso

        # Inserción en el subárbol izquierdo si la clave es menor
        if key < node.key:
            node.left = self._insert(node.left, key)
        # Inserción en el subárbol derecho si la clave es mayor
        else:
            node.right = self._insert(node.right, key)

        # Actualizar altura del nodo actual
        node.height = 1 + max(self.get_height(node.left), 
                            self.get_height(node.right))

        # Calcular factor de balance para ver si necesita rotación
        balance = self.get_balance(node)

        # Caso 1: Rotación simple a la derecha (left-left)
        if balance > 1 and key < node.left.key:
            return self.right_rotate(node)

        # Caso 2: Rotación simple a la izquierda (right-right)
        if balance < -1 and key > node.right.key:
            return self.left_rotate(node)

        # Caso 3: Rotación doble izquierda-derecha (left-right)
        if balance > 1 and key > node.left.key:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)

        # Caso 4: Rotación doble derecha-izquierda (right-left)
        if balance < -1 and key < node.right.key:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)

        return node  # Retorna el nodo (posiblemente modificado)

    def left_rotate(self, z):
        """
        Rotación izquierda para rebalancear el árbol.
        Args:
            z (AVLNode): Nodo desbalanceado
        Returns:
            AVLNode: Nueva raíz del subárbol
        """
        y = z.right  # y será la nueva raíz
        T2 = y.left  # Subárbol que cambiará de padre

        # Realizar rotación
        y.left = z
        z.right = T2

        # Actualizar alturas (primero z, luego y porque z ahora es hijo)
        z.height = 1 + max(self.get_height(z.left), 
                         self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), 
                         self.get_height(y.right))

        return y  # Retorna la nueva raíz

    def right_rotate(self, y):
        """
        Rotación derecha para rebalancear el árbol.
        Args:
            y (AVLNode): Nodo desbalanceado
        Returns:
            AVLNode: Nueva raíz del subárbol
        """
        x = y.left  # x será la nueva raíz
        T2 = x.right  # Subárbol que cambiará de padre

        # Realizar rotación
        x.right = y
        y.left = T2

        # Actualizar alturas (primero y, luego x porque y ahora es hijo)
        y.height = 1 + max(self.get_height(y.left), 
                         self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), 
                         self.get_height(x.right))

        return x  # Retorna la nueva raíz

    def get_height(self, node):
        """
        Obtiene la altura de un nodo.
        Args:
            node (AVLNode): Nodo a consultar
        Returns:
            int: Altura del nodo (0 si es None)
        """
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        """
        Calcula el factor de balance de un nodo.
        Args:
            node (AVLNode): Nodo a evaluar
        Returns:
            int: Diferencia de alturas (izq - der)
        """
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def inorder(self):
        """
        Recorrido inorder del árbol (izquierda, raíz, derecha).
        Returns:
            list: Lista de tuplas (ruta, frecuencia) ordenadas alfabéticamente
        """
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        """
        Método auxiliar recursivo para recorrido inorder.
        Args:
            node (AVLNode): Nodo actual
            result (list): Acumulador de resultados
        """
        if node:
            self._inorder(node.left, result)  # Visita izquierda
            result.append((node.key, node.freq))  # Procesa nodo actual
            self._inorder(node.right, result)  # Visita derecha

class AVLVisualizer:
    """
    Clase para visualizar gráficamente un árbol AVL usando networkx y matplotlib.
    """
    def draw(self, root):
        """
        Genera una visualización del árbol AVL.
        Args:
            root (AVLNode): Raíz del árbol a visualizar
        Returns:
            matplotlib.figure.Figure: Figura con el árbol dibujado
        """
        G = nx.DiGraph()  # Grafo dirigido (para mostrar jerarquía)
        pos = {}  # Diccionario de posiciones (x,y) de cada nodo

        def add_edges(node, x=0, y=0, dx=1.0):
            """
            Función recursiva para construir el grafo.
            Args:
                node (AVLNode): Nodo actual
                x (float): Posición x actual
                y (float): Posición y actual (nivel)
                dx (float): Espaciado horizontal
            """
            if node is None:
                return
            
            # Crear etiqueta con la ruta y su frecuencia
            label = f"{node.key}\nFreq: {node.freq}"
            G.add_node(label)
            pos[label] = (x, -y)  # Posicionar el nodo
            
            # Procesar hijo izquierdo (con posición desplazada a la izquierda)
            if node.left:
                left_label = f"{node.left.key}\nFreq: {node.left.freq}"
                G.add_edge(label, left_label)  # Agregar arista
                add_edges(node.left, x - dx, y + 1, dx / 2)  # Recursión
                
            # Procesar hijo derecho (con posición desplazada a la derecha)
            if node.right:
                right_label = f"{node.right.key}\nFreq: {node.right.freq}"
                G.add_edge(label, right_label)  # Agregar arista
                add_edges(node.right, x + dx, y + 1, dx / 2)  # Recursión

        # Construir el grafo comenzando desde la raíz
        add_edges(root)

        # Configurar la figura y dibujar
        fig, ax = plt.subplots(figsize=(12, 6))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', 
               node_size=2000, font_size=8, font_weight='bold', 
               arrows=True, ax=ax)
        ax.set_title("Árbol AVL de Rutas Frecuentes", fontsize=14)
        
        return fig  # Retornar la figura para su visualización
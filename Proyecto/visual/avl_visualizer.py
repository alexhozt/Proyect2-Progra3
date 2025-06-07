import matplotlib.pyplot as plt
import networkx as nx

class AVLNode:
    def __init__(self, key):
        self.key = key
        self.freq = 1
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if not node:
            return AVLNode(key)

        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            node.freq += 1
            return node

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        # Rotaciones
        if balance > 1 and key < node.left.key:
            return self.right_rotate(node)
        if balance < -1 and key > node.right.key:
            return self.left_rotate(node)
        if balance > 1 and key > node.left.key:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        if balance < -1 and key < node.right.key:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)

        return node

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append((node.key, node.freq))
            self._inorder(node.right, result)

class AVLVisualizer:
    def draw(self, root):
        G = nx.DiGraph()
        pos = {}

        def add_edges(node, x=0, y=0, dx=1.0):
            if node is None:
                return
            label = f"{node.key}\nFreq: {node.freq}"
            G.add_node(label)
            pos[label] = (x, -y)
            if node.left:
                left_label = f"{node.left.key}\nFreq: {node.left.freq}"
                G.add_edge(label, left_label)
                add_edges(node.left, x - dx, y + 1, dx / 2)
            if node.right:
                right_label = f"{node.right.key}\nFreq: {node.right.freq}"
                G.add_edge(label, right_label)
                add_edges(node.right, x + dx, y + 1, dx / 2)

        add_edges(root)

        fig, ax = plt.subplots(figsize=(12, 6))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000,
                font_size=8, font_weight='bold', arrows=True, ax=ax)
        ax.set_title("Árbol AVL de Rutas Frecuentes", fontsize=14)
        return fig

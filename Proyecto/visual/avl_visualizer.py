import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    def __init__(self, avl_tree):
        """
        param avl_tree: instancia del árbol AVL que almacena rutas más frecuentes
        """
        self.avl_tree = avl_tree
        self.G = nx.DiGraph()

    def draw(self):
        self.G.clear()
        self._build_graph(self.avl_tree.root)

        pos = self._hierarchy_pos(self.G, self.avl_tree.root.key if self.avl_tree.root else None)
        plt.figure(figsize=(12, 8))
        nx.draw(
            self.G,
            pos,
            with_labels=True,
            node_size=1500,
            node_color="#FFD700",
            font_size=8,
            font_weight='bold'
        )
        plt.title("Visualización del Árbol AVL de Rutas")
        plt.show()

    
    def _build_graph(self, node):
        if node is None:
            return
        
        label = f"{' → '.join(node.route)}\nFreq: {node.frequency}"
        self.G.add_node(node.key, label=label)

        if node.left:
            self.G.add_edge(node.key, node.left.key)
            self._build_graph(node.left)

        if node.right:
            self.G.add_edge(node.key, node.right.key)
            self._build_graph(node.right)


    def _hierarchy_pos(self, G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        """
        Recursivamente ubica nodos en forma jerárquica
        
        """
        if pos is None:
            pos = {} 
        
        pos[root] = (xcenter, vert_loc)
        neighbors = list(G.neighbors(root))
        if len(neighbors) != 0:
            dx = width / 2
            nextx = xcenter - width / 2
            for neighbor in neighbors:
                pos = self._hierarchy_pos(G, neighbor, width=dx, vert_gap=vert_gap,
                                          vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root)
                nextx += dx
        
        return pos
    


        


    



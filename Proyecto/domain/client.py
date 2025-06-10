import random
from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime

@dataclass
class Client:
    client_id: str
    name: str
    type: str  # "regular" o "premium"
    total_orders: int = 0
    created_at: str = None
    node_id: str = None  # ID del nodo asociado en el grafo
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)

class ClientManager:
    def __init__(self):
        self.clients = []
        self.client_by_node_id = {}  # Diccionario para búsqueda rápida
    
    def generate_clients(self, client_nodes: List) -> List[Client]:
        """Genera clientes asociados a nodos del grafo"""
        self.clients = []
        self.client_by_node_id = {}
        
        for i, node in enumerate(client_nodes, 1):
            client_id = f"C{str(i).zfill(3)}"
            name = f"Client{i}"
            client_type = "premium" if random.random() < 0.3 else "regular"
            
            client = Client(
                client_id=client_id,
                name=name,
                type=client_type,
                node_id=node.id  # Asociamos el ID del nodo
            )
            
            self.clients.append(client)
            self.client_by_node_id[node.id] = client
        
        return self.clients
    
    def get_client_by_node_id(self, node_id: str) -> Client:
        """Obtiene cliente por ID de nodo"""
        return self.client_by_node_id.get(node_id)
    
    def increment_order_count(self, node_id: str):
        """Incrementa contador de pedidos para un cliente"""
        client = self.get_client_by_node_id(node_id)
        if client:
            client.total_orders += 1
    
    def to_json(self) -> List[dict]:
        """Devuelve lista de clientes en formato JSON"""
        return [client.to_dict() for client in self.clients]
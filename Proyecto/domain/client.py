import random
from dataclasses import dataclass, asdict
from typing import List
from datetime import datetime

@dataclass
class Client:
    client_id: str
    name: str
    type: str  # "regular" o "premium"
    total_orders: int = 0
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)

class ClientManager:
    def __init__(self):
        self.clients = []
    
    def generate_clients(self, num_clients: int) -> List[Client]:
        """Genera una lista de clientes con IDs únicos y tipos aleatorios"""
        self.clients = []
        
        for i in range(1, num_clients + 1):
            client_id = f"C{str(i).zfill(3)}"
            name = f"Client{i}"
            client_type = "premium" if random.random() < 0.3 else "regular"  # 30% premium, 70% regular
            
            self.clients.append(Client(
                client_id=client_id,
                name=name,
                type=client_type
            ))
        
        return self.clients
    
    def get_client_by_id(self, client_id: str) -> Client:
        """Obtiene un cliente por su ID"""
        for client in self.clients:
            if client.client_id == client_id:
                return client
        return None
    
    def increment_order_count(self, client_id: str):
        """Incrementa el contador de pedidos para un cliente"""
        client = self.get_client_by_id(client_id)
        if client:
            client.total_orders += 1
    
    def to_json(self) -> List[dict]:
        """Devuelve la lista de clientes en formato JSON"""
        return [client.to_dict() for client in self.clients]
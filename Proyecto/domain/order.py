import uuid
import random
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime

@dataclass
class Order:
    order_id: str
    client: str
    client_id: str
    origin: str
    destination: str
    status: str  # "pending", "in_progress", "delivered", "cancelled"
    priority: int  # 0 (normal), 1 (alta), 2 (urgente)
    created_at: str
    delivered_at: Optional[str] = None
    route_cost: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)
    
    def mark_as_delivered(self):
        """Marca el pedido como entregado"""
        self.status = "delivered"
        self.delivered_at = datetime.now().isoformat()

class OrderManager:
    def __init__(self, clients: list):
        self.orders = []
        self.clients = clients
    
    def generate_initial_orders(self, num_orders: int, nodes: list) -> List[Order]:
        """Genera pedidos iniciales aleatorios"""
        self.orders = []
        
        # Filtrar nodos que son clientes (asumiendo que tienen type="cliente")
        client_nodes = [node for node in nodes if node.type == "cliente"]
        
        for _ in range(num_orders):
            # Seleccionar cliente aleatorio
            client_node = random.choice(client_nodes)
            client = next((c for c in self.clients if c.client_id == client_node.id), None)
            
            if not client:
                continue  # Si no encontramos el cliente, saltamos
                
            # Seleccionar origen y destino aleatorios (el destino debe ser diferente al origen)
            origin = random.choice([n for n in nodes if n.id != client_node.id]).id
            destination = client_node.id
            
            # Determinar prioridad (70% normal, 20% alta, 10% urgente)
            rand = random.random()
            if rand < 0.7:
                priority = 0
            elif rand < 0.9:
                priority = 1
            else:
                priority = 2
            
            self.orders.append(Order(
                order_id=str(uuid.uuid4()),
                client=client.name,
                client_id=client.client_id,
                origin=origin,
                destination=destination,
                status="pending",
                priority=priority,
                created_at=datetime.now().isoformat(),
                route_cost=None  # Se calculará más tarde
            ))
        
        return self.orders
    
    def get_pending_orders(self) -> List[Order]:
        """Obtiene todos los pedidos pendientes"""
        return [order for order in self.orders if order.status == "pending"]
    
    def to_json(self) -> List[dict]:
        """Devuelve la lista de pedidos en formato JSON"""
        return [order.to_dict() for order in self.orders]
    
    
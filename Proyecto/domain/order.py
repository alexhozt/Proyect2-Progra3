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
    node_id: str  # ID del nodo cliente en el grafo
    origin: str
    destination: str
    status: str
    priority: int
    created_at: str
    delivered_at: Optional[str] = None
    route_cost: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)
    

    def mark_as_delivered(self):
        self.status = "delivered"
        self.delivered_at = datetime.now().isoformat()

class OrderManager:
    def __init__(self, client_manager):
        self.orders = []
        self.client_manager = client_manager
    
    def generate_initial_orders(self, num_orders: int, client_nodes: list, all_nodes: list):
        """Genera pedidos iniciales asociados a nodos cliente"""
        self.orders = []
        
        for _ in range(num_orders):
            # Seleccionar nodo cliente aleatorio
            client_node = random.choice(client_nodes)
            client = self.client_manager.get_client_by_node_id(client_node.id)
            
            if not client:
                continue
                
            # Seleccionar origen (no puede ser el mismo nodo cliente)
            possible_origins = [n for n in all_nodes if n.id != client_node.id]
            origin_node = random.choice(possible_origins)
            
            # Determinar prioridad
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
                node_id=client_node.id,  # ID del nodo en el grafo
                origin=origin_node.id,
                destination=client_node.id,
                status="pending",
                priority=priority,
                created_at=datetime.now().isoformat()
                
            ))
        
        return self.orders
    
    def complete_order(self, order_id: str, route_cost: int):
        """Marca un pedido como completado y actualiza el cliente"""
        order = next((o for o in self.orders if o.order_id == order_id), None)
        if order:
            order.mark_as_delivered()
            order.route_cost = route_cost
            self.client_manager.increment_order_count(order.node_id)
    
    def get_pending_orders(self):
        return [o for o in self.orders if o.status == "pending"]
    
    def to_json(self):
        return [order.to_dict() for order in self.orders]
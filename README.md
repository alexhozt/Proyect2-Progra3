# Proyecto 1 de programacion III

Problematica:

Correos Chile ha decidido implementar una red de drones autónomos para mejorar su cobertura y reducir 
los tiempos de entrega. Esta decisión busca superar las limitaciones del transporte terrestre, afectado por 
congestión y rutas ineficientes. 

Como no existe una infraestructura aérea preexistente, el sistema debe ser diseñado completamente 
desde cero. Este sistema debe contemplar: 
    ● Centros de distribución (Almacenamiento): Puntos donde los drones recogen paquetes. 
    ● Estaciones de carga: Nodos estratégicos que los drones deben visitar para recargar si exceden 
    su autonomía. 
    ● Destinos de entrega (Clientes): Nodos dinámicos con prioridad asignada. Su ubicación y prioridad 
    pueden variar. 
    ● Rutas seguras: Las rutas deben ser viables considerando el consumo energético. Si el trayecto 
    excede el límite de autonomía, se debe forzar la visita a estaciones de recarga. 
    ● Registro de rutas: El sistema debe registrar la frecuencia de uso de rutas y nodos, para análisis 
    posterior. 
    ● Selección de rutas: A partir del registro anterior  se debe crear una heurística basada en 
    frecuencia que permita reutilizar rutas recurrentes a nodos más visitados, esto permitirá replicar 
    recorridos ya realizados. 

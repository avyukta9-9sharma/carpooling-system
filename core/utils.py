from collections import deque
from .models import Edge

def bfs(start_node, end_node):
    if start_node == end_node:
        return [start_node]

    visited = set()
    queue = deque([[start_node]])

    while queue:
        path = queue.popleft()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)

        neighbors = Edge.objects.filter(from_node=current).select_related('to_node')
        for edge in neighbors:
            new_path = path + [edge.to_node]
            if edge.to_node == end_node:
                return new_path
            queue.append(new_path)

    return None


def get_nodes_within_distance(node_list, max_distance=2):
    nearby = set()
    for node in node_list:
        visited = set()
        queue = deque([(node, 0)])
        while queue:
            current, dist = queue.popleft()
            if current in visited or dist > max_distance:
                continue
            visited.add(current)
            nearby.add(current)
            if dist < max_distance:
                neighbors = Edge.objects.filter(from_node=current).select_related('to_node')
                for edge in neighbors:
                    queue.append((edge.to_node, dist + 1))
    return nearby


def calculate_fare(route_nodes, pickup_index, dropoff_index, base_fee=2.0, unit_price=1.0):
    fare = base_fee
    passengers_per_hop = []

    for i in range(len(route_nodes) - 1):
        if pickup_index <= i < dropoff_index:
            passengers_per_hop.append(1)
        else:
            passengers_per_hop.append(0)

    n = sum(1 for p in passengers_per_hop if p > 0)
    if n == 0:
        return base_fee

    for i, p in enumerate(passengers_per_hop):
        if p > 0:
            fare += unit_price * (1 / n)

    return round(fare, 2)
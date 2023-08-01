import math
import numpy as np

def init_solution(n, dist_matrix): # hàm khởi tạo giải pháp ban đầu theo thuật toán tham lam
    visited = [1] + [0] * (n-1)
    route = [0]
    current_node = 0
    for _ in range(1,n): # tìm node tiếp theo gần với node hiện tại nhất
        next_node = -1
        min_dist = float('inf')
        visited[current_node] = 1
        for j in range(1,n):
            if visited[j] == 0 and min_dist > dist_matrix[current_node][j]:
                next_node = j
                min_dist = dist_matrix[current_node][j]
        current_node = next_node
        route.append(current_node)
    return route

def read_node_coords(file_path): # hàm đọc file tọa độ node và trả về ma trận cạnh
    with open(file_path, 'r') as f:
        lines = f.readlines()
    node_coords = []

    edge_weight_type = lines[0].split()[1]
    for i in range(1, lines.__len__()):
        line = lines[i]
        if line.strip() == 'NODE_COORD_SECTION':
            continue
        elif line.strip() == 'EOF':
            break
        else:
            node_id, x, y = line.strip().split()[0:3]
            node_coords.append((int(node_id), float(x), float(y)))

    return distance_matrix_from_node_coords(node_coords,edge_weight_type) # trả về danh sách các tọa độ


def distance_matrix_from_node_coords(node_coords,edge_weight_type): # hàm tính ma trận khoảng cách giữa các thành phố
    n = len(node_coords)
    dist_matrix = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i+1, n):
            x1, y1 = node_coords[i][1], node_coords[i][2]
            x2, y2 = node_coords[j][1], node_coords[j][2]
            if edge_weight_type == "EUC_2D": 
                dist = round(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))
            elif edge_weight_type == "ATT":
                dist = math.ceil(math.sqrt(((x1 - x2)**2 + (y1 - y2)**2)/10))
            dist_matrix[i][j] = dist_matrix[j][i] = dist
               
    return dist_matrix


def read_distance_matrix(file_path): # hàm đọc file ma trận khoảng cách và trả về ma trận cạnh
    dist_matrix = []
    with open(file_path, 'r') as file:
        start_parsing = False
        for line in file:
            if line.strip() == "EDGE_WEIGHT_SECTION":
                start_parsing = True
                continue
            if line.strip() == "EOF":
                break
            if start_parsing:
                row = list(map(int, line.split()))
                dist_matrix.append(row)
    
    return dist_matrix



def get_neighborhood(route): # hàm trả về danh sách các tuyến đường lân cận
    n = len(route)
    neighborhood = []
    for i in range(1, n-1):
        for j in range(i+1, n-1):
            new_route = route.copy()
            new_route[i], new_route[j] = new_route[j], new_route[i]
            neighborhood.append(new_route)
    
    return neighborhood


def fitness(route, dist_matrix): # hàm tính tổng khoảng cách của một tuyến đường
    total_dist = 0
    n = len(route)
    for i in range(n-1):
        total_dist += dist_matrix[route[i]][route[i+1]]
    total_dist += dist_matrix[route[n-1]][route[0]]
    
    return total_dist

# hàm thuật toán tìm kiếm tabu 
def tabu_search(dist_matrix, tabu_list_size=200, max_iterations=1500):
    n = len(dist_matrix)
    current_route = best_route = init_solution(n, dist_matrix)
    current_fitness = best_fitness = fitness(best_route, dist_matrix)
    tabu_list = []

    for _ in range(max_iterations):
        candidate_routes = get_neighborhood(current_route)
        best_tabu_candidate = None
        best_tabu_candidate_fitness = float('inf')

        best_candidate = None
        best_candidate_fitness = float('inf')
        
        # Tìm lời giải tốt nhất trong các lời giải láng giềng
        for candidate in candidate_routes:
            candidate_fitness = fitness(candidate, dist_matrix)

            if candidate in tabu_list:
                # print(candidate)
                if candidate_fitness < best_tabu_candidate_fitness:
                    best_tabu_candidate = candidate
                    best_tabu_candidate_fitness = candidate_fitness
                 
            else:
                if candidate_fitness < best_candidate_fitness:
                    best_candidate = candidate
                    best_candidate_fitness = candidate_fitness

        # Sử dụng điều kiện nguyện vọng (aspiration conditions)
        # Nếu giải pháp tabu tối ưu hơn thì chọn
        if best_tabu_candidate_fitness < best_candidate_fitness:
            tabu_list.remove(best_tabu_candidate)
            best_candidate = best_tabu_candidate
            best_candidate_fitness = best_tabu_candidate_fitness

        # Cập nhật lời giải tốt nhất nếu tìm được lời giải tốt hơn
        if best_candidate is not None:
            current_route = best_candidate
            current_fitness = best_candidate_fitness
            
            if current_fitness < best_fitness:
                best_fitness = current_fitness
                best_route = current_route
        
            
        # Thêm lời giải tốt nhất vào danh sách tabu
        tabu_list.append(current_route)
        
        if len(tabu_list) > tabu_list_size:
            tabu_list.pop(0)
        
    # Trả về tuyến đường và chi phí tốt nhất tìm được
    return best_route, best_fitness

filepath = "ry48p(ATSP).txt"
dist_matrix = read_distance_matrix(filepath)

print(tabu_search(dist_matrix))


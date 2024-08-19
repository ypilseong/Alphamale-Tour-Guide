import osmnx as ox
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import simplekml  # KML 파일 저장을 위한 라이브러리

def route_optimization(strat_point=(33.510414, 126.492028), 
                       waypoints=[
            (33.36080038544294, 126.60472066132864),  
            (33.505485934, 126.534739654),            
            (33.210151052, 126.257153778),            
            (33.390805591, 126.366270031),            
            (33.46232863, 126.310472423),             
            (33.526804054, 126.588622862),            
            (33.35733879962504, 126.4628821048391),   
            (33.357533041, 126.462547934),            
            (33.439337842, 126.629988029),            
            (33.509829919, 126.519546904)],
                        end_point=(33.480073809, 126.473476368)):
    # GUI가 없는 환경에서 사용하기 위해 'Agg' 백엔드를 설정
    matplotlib.use('Agg')

    # 제주도의 도로 네트워크를 불러옵니다.
    place_name = "Jeju Island, South Korea"
    graph = ox.graph_from_place(place_name, network_type="drive")

    

    # 모든 경유지 포함하여 경로를 찾기 위해, 출발점과 경유지, 도착지를 한 리스트에 저장합니다.
    points = [strat_point] + waypoints + [end_point]

    # 각 지점을 그래프에서 가장 가까운 노드로 변환합니다.
    nodes = [ox.distance.nearest_nodes(graph, X=point[1], Y=point[0]) for point in points]

    # 경로를 순차적으로 계산하여 연결합니다.
    full_route = []
    for i in range(len(nodes) - 1):
        route_segment = nx.shortest_path(graph, nodes[i], nodes[i + 1], weight='length')
        if full_route:
            full_route += route_segment[1:]  # 중복되는 노드 제거
        else:
            full_route = route_segment

    # 경로를 시각화한 이미지를 PNG 파일로 저장합니다.
    fig, ax = ox.plot_graph_route(graph, full_route, route_linewidth=6, node_size=0, bgcolor='k', save=False, show=False)
    fig.savefig("full_route_with_waypoints.png", dpi=300)

    # 경로를 KML 파일로 저장하기 위해 노드들의 위도/경도를 가져옵니다.
    route_latlng = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in full_route]

    # KML 파일 생성을 위한 KML 객체 생성
    kml = simplekml.Kml()

    # KML 경로 추가 (LineString)
    linestring = kml.newlinestring(name="Route with waypoints")
    linestring.coords = [(lng, lat) for lat, lng in route_latlng]  # KML은 (경도, 위도) 형식으로 좌표가 필요
    linestring.style.linestyle.width = 5  # 선의 두께
    linestring.style.linestyle.color = simplekml.Color.red  # 선 색상 (빨강)

    # 경유지마다 핀포인트 추가
    for idx, point in enumerate(points):
        pnt = kml.newpoint(name=str(idx + 1), coords=[(point[1], point[0])])  # (경도, 위도)
        pnt.style.labelstyle.color = simplekml.Color.red  # 라벨 색상
        pnt.style.labelstyle.scale = 1.5  # 라벨 크기
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'  # 핀 아이콘 설정

    # KML 파일 저장
    kml.save("src/alphamale_tour_guide/route_opt/jeju_routes5.kml")

    print("KML 파일이 저장되었습니다: src/alphamale_tour_guide/route_opt/jeju_routes.kml")

if __name__ == "__main__":
    route_optimization()
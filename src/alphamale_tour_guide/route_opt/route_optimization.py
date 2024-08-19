import osmnx as ox
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import simplekml  # KML 파일 저장을 위한 라이브러리

# 색상 리스트 정의
colors = [
    'fffff8f0',  # aliceblue
    'ffd7ebfa',  # antiquewhite
    'ffffff00',  # aqua
    'ffd4ff7f',  # aquamarine
    'fffffff0',  # azure
    'ffdcf5f5',  # beige
    'ffc4e4ff',  # bisque
    'ff000000',  # black
    'ffcdebff',  # blanchedalmond
    'ffff0000',  # blue
    'ffe22b8a',  # blueviolet
    'ff2a2aa5',  # brown
    'ff87b8de',  # burlywood
    'ffa09e5f',  # cadetblue
]

def is_valid_coordinate(coord):
    """좌표가 유효한지 확인하는 함수."""
    try:
        lat, lon = coord
        return isinstance(lat, (float, int)) and isinstance(lon, (float, int))
    except:
        return False

def route_optimization(days_coordinates):
    # GUI가 없는 환경에서 사용하기 위해 'Agg' 백엔드를 설정
    matplotlib.use('Agg')

    # 제주도의 도로 네트워크를 불러옵니다.
    place_name = "Jeju Island, South Korea"
    graph = ox.graph_from_place(place_name, network_type="drive")

    # KML 파일 생성을 위한 KML 객체 생성
    kml = simplekml.Kml()

    # 모든 일차에 대해 경로 최적화 수행
    for day_index, (day, coordinates) in enumerate(days_coordinates.items()):
        # 유효한 좌표만 필터링
        valid_points = [coord for coord in coordinates if is_valid_coordinate(coord)]

        if len(valid_points) < 2:
            print(f"Warning: Day {day} has insufficient valid coordinates.")
            continue

        # 시작점, 경유지, 종료점을 설정
        start_point = valid_points[0]
        end_point = valid_points[-1]
        waypoints = valid_points[1:-1] if len(valid_points) > 2 else []

        try:
            # 각 지점을 그래프에서 가장 가까운 노드로 변환합니다.
            nodes = [ox.distance.nearest_nodes(graph, X=point[1], Y=point[0]) for point in valid_points]

            # 경로를 순차적으로 계산하여 연결합니다.
            full_route = []
            for i in range(len(nodes) - 1):
                route_segment = nx.shortest_path(graph, nodes[i], nodes[i + 1], weight='length')
                if full_route:
                    full_route += route_segment[1:]  # 중복되는 노드 제거
                else:
                    full_route = route_segment

            # 색상 순환 적용
            route_color = colors[day_index % len(colors)]

            # 경로를 시각화한 이미지를 PNG 파일로 저장합니다.
            fig, ax = ox.plot_graph_route(graph, full_route, route_linewidth=6, node_size=0, bgcolor='k', route_color='#' + route_color, save=False, show=False)
            fig.savefig(f"full_route_with_waypoints_day_{day}.png", dpi=300)

            # 경로를 KML 파일로 저장하기 위해 노드들의 위도/경도를 가져옵니다.
            route_latlng = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in full_route]

            # KML 경로 추가 (LineString)
            linestring = kml.newlinestring(name=f"Route Day {day}")
            linestring.coords = [(lng, lat) for lat, lng in route_latlng]  # KML은 (경도, 위도) 형식으로 좌표가 필요
            linestring.style.linestyle.width = 5  # 선의 두께
            linestring.style.linestyle.color = route_color  # 지정된 색상 사용
            linestring.style.colormode = simplekml.ColorMode.normal  # 색상 모드 설정

            # 경유지마다 핀포인트 추가
            for idx, point in enumerate(valid_points):
                pnt = kml.newpoint(name=f"{day}-{idx + 1}", coords=[(point[1], point[0])])  # (경도, 위도)
                pnt.style.labelstyle.color = route_color  # 라벨 색상
                pnt.style.labelstyle.scale = 1.5  # 라벨 크기
                pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'  # 핀 아이콘 설정
                pnt.style.colormode = simplekml.ColorMode.normal  # 색상 모드 설정

        except Exception as e:
            print(f"Error processing Day {day}: {e}")
            continue

    # KML 파일 저장
    kml.save("src/alphamale_tour_guide/route_opt/jeju_routes_optimized.kml")

    print("KML 파일이 저장되었습니다: src/alphamale_tour_guide/route_opt/jeju_routes_optimized.kml")

if __name__ == "__main__":
    # 예시 데이터: 각 일차별 좌표 리스트
    days_coordinates = {
        1: [
            (33.510414, 126.492028),  # start_point
            (33.36080038544294, 126.60472066132864),  
            (33.505485934, 126.534739654),            
            (33.210151052, 126.257153778),            
            (33.390805591, 126.366270031),            
            (33.46232863, 126.310472423),             
            (33.526804054, 126.588622862),            
            (33.35733879962504, 126.4628821048391),   
            (33.357533041, 126.462547934),            
            (33.439337842, 126.629988029),            
            (33.509829919, 126.519546904),            # end_point
        ],
        2: [
            (33.480073809, 126.473476368),  # start_point
            (33.36080038544294, 126.60472066132864),  
            (33.505485934, 126.534739654),            
            (33.210151052, 126.257153778),            
            (33.390805591, 126.366270031),            
            (33.46232863, 126.310472423),             
            (33.526804054, 126.588622862),            
            (33.35733879962504, 126.4628821048391),   
            (33.357533041, 126.462547934),            
            (33.439337842, 126.629988029),            
            (33.509829919, 126.519546904),            # end_point
        ]
    }

    route_optimization(days_coordinates)

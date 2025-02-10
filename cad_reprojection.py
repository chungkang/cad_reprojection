import ezdxf
from pyproj import Transformer

# 입력 및 출력 좌표계 정의 (EPSG 코드 사용)
input_crs = "EPSG:5187"
output_crs = "EPSG:5174"

# 좌표 변환기 설정
transformer = Transformer.from_crs(input_crs, output_crs, always_xy=True)

# DXF 파일 열기
input_dxf = "sample/sample02_EPSG5187.dxf"
output_dxf = "out_sample02_EPSG5174.dxf"
doc = ezdxf.readfile(input_dxf)
msp = doc.modelspace()

# DXF 엔티티 순회 및 좌표 변환
def transform_entity(entity):
    """ 엔티티의 좌표를 변환하는 함수 """
    
    if entity.dxftype() == "LINE":
        # LINE의 시작점과 끝점 변환
        x1, y1 = transformer.transform(entity.dxf.start.x, entity.dxf.start.y)
        x2, y2 = transformer.transform(entity.dxf.end.x, entity.dxf.end.y)
        print(f"LINE 변환: ({entity.dxf.start.x}, {entity.dxf.start.y}) -> ({x1}, {y1})")
        print(f"LINE 변환: ({entity.dxf.end.x}, {entity.dxf.end.y}) -> ({x2}, {y2})")
        entity.dxf.start = (x1, y1)
        entity.dxf.end = (x2, y2)

    elif entity.dxftype() == "LWPOLYLINE":
        # LWPOLYLINE의 점 목록 변환 (bulge 값 포함 처리)
        points = []
        with entity.points() as point_iter:
            for p in point_iter:
                # p[0]과 p[1]은 좌표, p[2:]는 나머지 bulge 값
                new_point = (transformer.transform(p[0], p[1])[0], 
                            transformer.transform(p[0], p[1])[1], *p[2:])
                points.append(new_point)
        print(f"LWPOLYLINE 변환: {points}")
        entity.set_points(points)

    elif entity.dxftype() == "POLYLINE":
        # POLYLINE의 점 변환 (vertex를 하나씩 변환)
        for vertex in entity.vertices:
            x, y = transformer.transform(vertex.dxf.location.x, vertex.dxf.location.y)
            print(f"POLYLINE vertex 변환: ({vertex.dxf.location.x}, {vertex.dxf.location.y}) -> ({x}, {y})")
            vertex.dxf.location = (x, y)

    elif entity.dxftype() in ["CIRCLE", "ARC"]:
        # CIRCLE, ARC의 중심점 변환
        x, y = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
        print(f"CIRCLE/ARC 변환: ({entity.dxf.center.x}, {entity.dxf.center.y}) -> ({x}, {y})")
        entity.dxf.center = (x, y)

    elif entity.dxftype() == "INSERT":
        # 블록(INSERT)의 인서트 포인트 변환
        x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
        print(f"INSERT 변환: ({entity.dxf.insert.x}, {entity.dxf.insert.y}) -> ({x}, {y})")
        entity.dxf.insert = (x, y)

    elif entity.dxftype() == "TEXT":
        # TEXT의 인서트 포인트 변환
        x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
        print(f"TEXT 변환: ({entity.dxf.insert.x}, {entity.dxf.insert.y}) -> ({x}, {y})")
        entity.dxf.insert = (x, y)

    elif entity.dxftype() == "MTEXT":
        # MTEXT의 인서트 포인트 변환
        x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
        print(f"MTEXT 변환: ({entity.dxf.insert.x}, {entity.dxf.insert.y}) -> ({x}, {y})")
        entity.dxf.insert = (x, y)

# 모델 공간의 모든 엔티티 변환
for entity in msp:
    transform_entity(entity)

# 변환된 DXF 저장
doc.saveas(output_dxf)
print(f"변환된 DXF 저장 완료: {output_dxf}")

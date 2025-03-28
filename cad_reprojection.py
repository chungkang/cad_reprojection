import ezdxf
from pyproj import Transformer
import tkinter as tk
from tkinter import filedialog, messagebox
import math  # math 모듈 추가

def transform_dxf(input_dxf, output_dxf, input_crs, output_crs):
    """DXF 파일의 좌표계를 변환하는 함수"""
    try:
        transformer = Transformer.from_crs(input_crs, output_crs, always_xy=True)
        doc = ezdxf.readfile(input_dxf)
        msp = doc.modelspace()

        def transform_entity(entity):
            if entity.dxftype() == "LINE":
                x1, y1 = transformer.transform(entity.dxf.start.x, entity.dxf.start.y)
                x2, y2 = transformer.transform(entity.dxf.end.x, entity.dxf.end.y)
                entity.dxf.start = (x1, y1)
                entity.dxf.end = (x2, y2)

            elif entity.dxftype() == "LWPOLYLINE":
                points = [(transformer.transform(p[0], p[1])[0], transformer.transform(p[0], p[1])[1], *p[2:]) for p in list(entity.get_points())]
                entity.set_points(points)

            elif entity.dxftype() == "POLYLINE":
                for vertex in list(entity.vertices()):
                    x, y = transformer.transform(vertex.dxf.location.x, vertex.dxf.location.y)
                    vertex.dxf.location = (x, y)

            elif entity.dxftype() in ["CIRCLE", "ARC"]:
                x, y = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
                entity.dxf.center = (x, y)
                if entity.dxftype() == "ARC":
                    # ArcEdge 처리: 중심점과 반지름을 변환
                    center_x, center_y = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
                    entity.dxf.center = (center_x, center_y)
                    
                    # 시작점과 끝점을 계산하여 변환
                    start_angle = entity.dxf.start_angle
                    end_angle = entity.dxf.end_angle
                    radius = entity.dxf.radius
                    
                    start_x, start_y = transformer.transform(entity.dxf.center.x + radius * math.cos(start_angle), entity.dxf.center.y + radius * math.sin(start_angle))
                    end_x, end_y = transformer.transform(entity.dxf.center.x + radius * math.cos(end_angle), entity.dxf.center.y + radius * math.sin(end_angle))

                    # 새로운 점을 적용 (start_point와 end_point를 직접 설정하는 대신 start, end 사용)
                    entity.dxf.start = (start_x, start_y)
                    entity.dxf.end = (end_x, end_y)

            elif entity.dxftype() == "INSERT":
                x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
                entity.dxf.insert = (x, y)

            elif entity.dxftype() in ["TEXT", "MTEXT"]:
                x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
                entity.dxf.insert = (x, y)

                # align_point (정렬점) 속성이 존재할 경우 변환
                if entity.dxf.hasattr("align_point"):
                    ax, ay = transformer.transform(entity.dxf.align_point.x, entity.dxf.align_point.y)
                    entity.dxf.align_point = (ax, ay)

            elif entity.dxftype() == "POINT":
                x, y = transformer.transform(entity.dxf.location.x, entity.dxf.location.y)
                entity.dxf.location = (x, y)

            elif entity.dxftype() == "HATCH":
                for boundary in entity.paths:
                    # 각 경로에 대해 점들을 변환
                    for path in boundary:
                        if isinstance(path, ezdxf.entities.LineEdge):
                            # LineEdge 처리
                            x1, y1 = transformer.transform(path.start.x, path.start.y)
                            x2, y2 = transformer.transform(path.end.x, path.end.y)
                            path.start = (x1, y1)
                            path.end = (x2, y2)
                        elif isinstance(path, ezdxf.entities.ArcEdge):
                            # ArcEdge 처리 (호의 좌표 변환)
                            center_x, center_y = transformer.transform(path.center.x, path.center.y)
                            start_angle = path.start_angle
                            end_angle = path.end_angle
                            radius = path.radius
                            
                            start_x, start_y = transformer.transform(path.center.x + radius * math.cos(start_angle), path.center.y + radius * math.sin(start_angle))
                            end_x, end_y = transformer.transform(path.center.x + radius * math.cos(end_angle), path.center.y + radius * math.sin(end_angle))

                            # start_point와 end_point를 직접 설정하지 않고 start와 end 속성을 수정
                            path.start = (start_x, start_y)
                            path.end = (end_x, end_y)
                        else:
                            for vertex in path:
                                x, y = transformer.transform(vertex[0], vertex[1])
                                vertex[0] = x
                                vertex[1] = y

            elif entity.dxftype() == "IMAGE":
                # 이미지 엔티티의 좌표도 변환 (일반적으로 insert 속성 사용)
                if hasattr(entity.dxf, "insert"):
                    x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
                    entity.dxf.insert = (x, y)

        for entity in msp:
            transform_entity(entity)

        doc.saveas(output_dxf)
        messagebox.showinfo("완료", f"변환된 DXF 저장 완료: {output_dxf}")
    except Exception as e:
        messagebox.showerror("오류", str(e))


def select_input_dxf():
    filename = filedialog.askopenfilename(filetypes=[("DXF Files", "*.dxf")])
    if filename:  # 파일이 선택된 경우에만
        input_dxf_entry.delete(0, tk.END)
        input_dxf_entry.insert(0, filename)


def select_output_dxf():
    filename = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF Files", "*.dxf")])
    if filename:  # 파일이 선택된 경우에만
        output_dxf_entry.delete(0, tk.END)
        output_dxf_entry.insert(0, filename)


def start_conversion():
    input_dxf = input_dxf_entry.get()
    output_dxf = output_dxf_entry.get()
    input_crs = input_crs_entry.get()
    output_crs = output_crs_entry.get()
    
    if not input_dxf or not output_dxf or not input_crs or not output_crs:
        messagebox.showerror("오류", "모든 항목을 입력해야 합니다.")
        return
    
    transform_dxf(input_dxf, output_dxf, input_crs, output_crs)

# GUI 생성
root = tk.Tk()
root.title("DXF 좌표 변환기")
root.geometry("500x220")
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="입력좌표계(예시: EPSG:5186):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
input_crs_entry = tk.Entry(frame, width=30)
input_crs_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame, text="출력좌표계(예시: EPSG:5174):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
output_crs_entry = tk.Entry(frame, width=30)
output_crs_entry.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame, text="입력 DXF 파일:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
input_dxf_entry = tk.Entry(frame, width=30)
input_dxf_entry.grid(row=2, column=1, padx=5, pady=2)
tk.Button(frame, text="찾기", command=select_input_dxf).grid(row=2, column=2, padx=5, pady=2)

tk.Label(frame, text="출력 DXF 파일:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
output_dxf_entry = tk.Entry(frame, width=30)
output_dxf_entry.grid(row=3, column=1, padx=5, pady=2)
tk.Button(frame, text="저장위치", command=select_output_dxf).grid(row=3, column=2, padx=5, pady=2)

warning_label = tk.Label(root, text="※ GIS 프로그램의 좌표 변환 방식과 차이가 있을 수 있으며,\n   변환 과정에서 오차가 발생할 수 있습니다.", fg="red")
warning_label.pack(pady=5)

tk.Button(root, text="변환 실행", command=start_conversion, bg="blue", fg="white").pack(pady=10)

root.mainloop()

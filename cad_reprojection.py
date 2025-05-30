import ezdxf
from pyproj import Transformer
import tkinter as tk
from tkinter import filedialog, messagebox
import math


def transform_dxf(input_dxf, output_dxf, input_crs, output_crs):
    """DXF 파일의 좌표계를 변환하는 함수"""
    try:
        transformer = Transformer.from_crs(input_crs, output_crs, always_xy=True)
        doc = ezdxf.readfile(input_dxf)
        msp = doc.modelspace()

        def transform_entity(entity):
            dxftype = entity.dxftype()

            # === 복잡한 엔티티 수동 처리 ===
            if dxftype == "ARC":
                cx, cy = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
                entity.dxf.center = (cx, cy)

            elif dxftype == "LWPOLYLINE":
                points = [
                    (*transformer.transform(x, y), *point[2:])
                    for x, y, *point in entity.get_points()
                ]
                entity.set_points(points)

            elif dxftype == "POLYLINE":
                vertices = entity.vertices if isinstance(entity.vertices, list) else entity.vertices()
                for vertex in vertices:
                    x, y = transformer.transform(vertex.dxf.location.x, vertex.dxf.location.y)
                    vertex.dxf.location = (x, y)

            elif dxftype == "HATCH":
                for path in entity.paths:
                    if hasattr(path, "edges"):
                        # EdgePath 처리
                        for edge in path.edges:
                            if isinstance(edge, ezdxf.entities.LineEdge):
                                x1, y1 = transformer.transform(edge.start.x, edge.start.y)
                                x2, y2 = transformer.transform(edge.end.x, edge.end.y)
                                edge.start = (x1, y1)
                                edge.end = (x2, y2)
                            elif isinstance(edge, ezdxf.entities.ArcEdge):
                                cx, cy = transformer.transform(edge.center.x, edge.center.y)
                                edge.center = (cx, cy)
                    elif hasattr(path, "vertices"):
                        # PolylinePath 처리
                        new_vertices = []
                        for x, y, *rest in path.vertices:
                            x_t, y_t = transformer.transform(x, y)
                            new_vertices.append((x_t, y_t, *rest))
                        path.vertices = new_vertices

            elif dxftype == "MTEXT":
                if hasattr(entity.dxf, "insert"):
                    x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
                    entity.dxf.insert = (x, y)
                if entity.dxf.hasattr("align_point"):
                    ax, ay = transformer.transform(entity.dxf.align_point.x, entity.dxf.align_point.y)
                    entity.dxf.align_point = (ax, ay)

            elif dxftype == "LEADER":
                vertices = entity.vertices if isinstance(entity.vertices, list) else entity.vertices()
                new_vertices = []
                for vertex in vertices:
                    x, y = transformer.transform(vertex[0], vertex[1])
                    if len(vertex) == 3:
                        z = vertex[2]
                        new_vertices.append((x, y, z))
                    else:
                        new_vertices.append((x, y))
                entity.vertices = new_vertices

            elif dxftype == "IMAGE":
                x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
                entity.dxf.insert = (x, y)

            elif dxftype == "ELLIPSE":
                # 중심 좌표 변환
                cx, cy = transformer.transform(entity.dxf.center.x, entity.dxf.center.y)
                entity.dxf.center = (cx, cy)

                # 주축 벡터 변환 (벡터는 위치가 아닌 방향 → 회전만 적용해야 하는데 실제로는 길이까지 고려됨)
                # 단순 좌표 변환이 아닌 상대적 이동량만 적용해야 정확함
                mx, my = entity.dxf.major_axis.x, entity.dxf.major_axis.y
                dx1, dy1 = transformer.transform(cx + mx, cy + my)
                dx0, dy0 = cx, cy
                new_major_axis = (dx1 - dx0, dy1 - dy0)

                entity.dxf.major_axis = new_major_axis

            # === 단순한 엔티티는 자동 처리 ===
            else:
                for attr in dir(entity.dxf):
                    if attr.startswith('__') or attr in ('center', 'major_axis'):
                        continue
                    try:
                        val = getattr(entity.dxf, attr)
                        if isinstance(val, ezdxf.math.Vec2) or isinstance(val, ezdxf.math.Vec3):
                            x, y = transformer.transform(val.x, val.y)
                            z = val.z if hasattr(val, 'z') else 0
                            new_vec = ezdxf.math.Vec3(x, y, z) if hasattr(val, 'z') else ezdxf.math.Vec2(x, y)
                            setattr(entity.dxf, attr, new_vec)
                    except Exception:
                        continue

        for entity in msp:
            transform_entity(entity)

        doc.saveas(output_dxf)
        messagebox.showinfo("완료", f"변환된 DXF 저장 완료: {output_dxf}")
    except Exception as e:
        messagebox.showerror("오류", str(e))


def select_input_dxf():
    filename = filedialog.askopenfilename(filetypes=[("DXF Files", "*.dxf")])
    if filename:
        input_dxf_entry.delete(0, tk.END)
        input_dxf_entry.insert(0, filename)


def select_output_dxf():
    filename = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF Files", "*.dxf")])
    if filename:
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
root.geometry("500x250")
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

info_label = tk.Label(root, text="자세한 사항은 https://github.com/chungkang/cad_reprojection 페이지를 참고하세요.", fg="blue", cursor="hand2")
info_label.pack()

# 클릭 시 웹 브라우저로 이동하도록 설정
def open_github(event):
    import webbrowser
    webbrowser.open_new("https://github.com/chungkang/cad_reprojection")

info_label.bind("<Button-1>", open_github)

tk.Button(root, text="변환 실행", command=start_conversion, bg="blue", fg="white").pack(pady=10)

root.mainloop()

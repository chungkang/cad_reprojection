import ezdxf
from pyproj import Transformer
import tkinter as tk
from tkinter import filedialog, messagebox

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

            elif entity.dxftype() == "INSERT":
                x, y = transformer.transform(entity.dxf.insert.x, entity.dxf.insert.y)
                entity.dxf.insert = (x, y)

            elif entity.dxftype() in ["TEXT", "MTEXT"]:
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
    if filename.endswith(".dxf"):
        input_dxf_entry.delete(0, tk.END)
        input_dxf_entry.insert(0, filename)
    else:
        messagebox.showerror("오류", "DXF 파일만 선택할 수 있습니다.")


def select_output_dxf():
    filename = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF Files", "*.dxf")])
    if filename.endswith(".dxf"):
        output_dxf_entry.delete(0, tk.END)
        output_dxf_entry.insert(0, filename)
    else:
        messagebox.showerror("오류", "DXF 파일만 저장할 수 있습니다.")


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

warning_label = tk.Label(root, text="※ GIS 프로그램의 좌표 변환 방식과 차이가 있을 수 있으며,\n   변환 과정에서 ~0.005m 오차가 발생할 수 있습니다.", fg="red")
warning_label.pack(pady=5)

tk.Button(root, text="변환 실행", command=start_conversion, bg="blue", fg="white").pack(pady=10)

root.mainloop()

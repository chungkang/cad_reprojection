CAD file(dxf) reprojection


pip install pyinstaller


pyinstaller --onefile --noconsole --icon=convert_d_cube_icon_240710.ico cad_reprojection.py
rm -rf build __pycache__ cad_reprojection.spec


복잡한 구조는 안전하게 수동 처리

나머지는 .dxf 내부 속성 자동 탐색으로 일괄 좌표 변환

Arc, Hatch 등은 여전히 수동 처리 권장 (모양 깨질 수 있음)

안정성 + 범용성 모두 챙긴 구조
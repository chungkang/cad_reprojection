CAD file(dxf) reprojection


pip install pyinstaller


pyinstaller --onefile --noconsole --icon=convert_d_cube_icon_240710.ico cad_reprojection.py
rm -rf build __pycache__ cad_reprojection.spec

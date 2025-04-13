# 🧭 Cad_Reprojection

**Cad_Reprojection**은 Python과 `ezdxf` 라이브러리를 기반으로 DXF (CAD) 파일의 좌표계(CRS, Coordinate Reference System) 변환을 수행하는 개인 프로젝트입니다.  
GIS 업무에서 자주 필요한 **CAD 도면의 좌표계 변환 작업을 간소화**하고자 개발되었습니다.

> 📌 DXF → 다른 좌표계로 자동 변환하는 **Windows GUI 프로그램**입니다.  
> AutoCAD에서 제공되지 않는 CRS 변환 기능을 대신합니다.



## 🛠️ 주요 기능

- `.dxf` 형식의 CAD 도면의 좌표계를 자동으로 변환
- GUI 기반으로 누구나 사용하기 쉬움 (`tkinter`)
- **복잡한 엔티티는 수동 처리 권장**, 단순 요소는 자동 처리
- **Arc, Hatch** 등 일부 요소는 형상 손실 우려로 수동 확인 필요



## 🧪 사용 기술

- **Python**
- [ezdxf](https://github.com/mozman/ezdxf)
- [pyproj](https://pyproj4.github.io/pyproj/)
- `tkinter` GUI




## 💻 실행 방법

### 1. EXE 파일 실행 (추천)

현재 빌드된 실행 파일(`cad_reprojection.exe`)이 이 저장소에 포함되어 있습니다.  
별도 설치 없이 Windows 환경에서 바로 실행 가능합니다.

### 2. 소스코드 실행

1. Python이 설치되어 있어야 합니다.
2. 의존성 설치:

   ```bash
   pip install ezdxf pyproj

3. 아래 명령어로 실행:

   ```bash
   python cad_reprojection.py

## 📦 EXE 파일 빌드하기 (선택)

pyinstaller를 통해 .exe 파일로 패키징할 수 있습니다:

1. pyinstaller 설치:

   ```bash
   pip install pyinstaller

2. EXE 빌드 실행:

   ```bash
   pyinstaller --onefile --noconsole --icon=convert_d_cube_icon_240710.ico cad_reprojection.py
   rm -rf build __pycache__ cad_reprojection.spec

## 📂 GUI 구성
  입력 CRS (예: EPSG:5186)
  
  출력 CRS (예: EPSG:5174)
  
  입력 DXF 파일 선택
  
  출력 파일 저장 경로

  변환 버튼 클릭 → 자동 좌표 변환 및 저장

### ⚠️ 좌표 변환 오차나 일부 객체의 누락 가능성이 있으므로 결과물을 AutoCAD 등에서 추가 검토하는 것이 좋습니다.

### ⚠️ 주의사항
  - Arc, Hatch, Spline 등 일부 복잡한 엔티티는 자동 변환 시 형상이 깨질 수 있어 수동 처리 권장

  - EPSG 코드 입력 오류 시 실행되지 않음

  - GIS 소프트웨어와 변환 방식이 다를 수 있음

## 📝 라이선스
  이 프로젝트는 MIT 라이선스를 따릅니다.

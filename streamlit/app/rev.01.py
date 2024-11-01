# ultralytics 패키지 설치 안해서 아직 기능을 하는지 확인 불가함

'''
**폴더 및 파일 경로 설정 방법:**

- **사용자가 업로드하는 이미지를 저장하기 위한 폴더:**

  `app.py` 파일이 있는 디렉토리 내에 `uploads` 폴더를 생성하세요.

  ```
  /home/dataiku/workspace/code_studio-versioned/streamlit/uploads/
  ```

- **`best.pt` 저장 위치:**

  `app.py` 상위 디렉토리에 `models` 폴더를 생성하고, 그 안에 `best.pt` 파일을 저장하세요.

  ```
  /home/dataiku/workspace/code_studio-versioned/models/best.pt
  ```

- **검출 후 bounding box가 추가된 이미지를 저장하는 폴더:**

  `app.py` 파일이 있는 디렉토리 내에 `detected` 폴더를 생성하세요.

  ```
  /home/dataiku/workspace/code_studio-versioned/streamlit/detected/
  ```

**추가 설명:**

- **모델 로드:** `ultralytics` 패키지를 사용하여 YOLOv8 모델을 로드합니다. 모델 파일 `best.pt`는 `models` 폴더에 저장되어 있어야 합니다.

- **이미지 처리 흐름:**

  1. 사용자가 이미지를 업로드하면 `uploads` 폴더에 저장됩니다.
  2. 업로드된 이미지를 모델에 입력하여 객체 검출을 수행합니다.
  3. 검출 결과 이미지는 `detected` 폴더에 저장됩니다.
  4. 원본 이미지와 검출 결과 이미지를 Streamlit 앱에서 표시합니다.

- **폴더 생성:** 코드에서 `os.makedirs()` 함수를 사용하여 필요한 폴더가 없을 경우 자동으로 생성되도록 합니다.

**주의 사항:**

- **패키지 설치:** `ultralytics`와 `streamlit` 패키지가 설치되어 있어야 합니다. 필요에 따라 `pip install ultralytics streamlit` 명령을 사용하여 설치하세요.

- **파일 권한:** 해당 디렉토리에 대한 읽기/쓰기 권한이 있어야 합니다.

이렇게 설정하시면, Streamlit 앱을 통해 사용자가 이미지를 업로드하고 객체 검출 결과를 확인할 수 있습니다.

'''

import streamlit as st
from PIL import Image
import os
from ultralytics import YOLO

# 현재 디렉토리 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 폴더 경로 설정
UPLOAD_FOLDER = os.path.join(CURRENT_DIR, 'uploads')
DETECTED_FOLDER = os.path.join(CURRENT_DIR, 'detected')
MODEL_PATH = os.path.join(CURRENT_DIR, '..', 'models', 'best.pt')

# 폴더가 없으면 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DETECTED_FOLDER, exist_ok=True)

# YOLOv8 모델 로드
model = YOLO(MODEL_PATH)

# Streamlit 앱 시작
st.title('객체 검출 앱')

# 이미지 업로드 위젯
uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 업로드된 파일 저장
    img = Image.open(uploaded_file).convert('RGB')
    img_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    img.save(img_path)

    # 객체 검출 실행
    results = model(img_path)

    # 검출된 이미지 저장
    detected_img_path = os.path.join(DETECTED_FOLDER, uploaded_file.name)
    detected_img = results[0].plot()  # numpy array 반환
    detected_img_pil = Image.fromarray(detected_img)
    detected_img_pil.save(detected_img_path)

    # 이미지 출력
    st.image(img, caption='업로드된 이미지', use_column_width=True)
    st.image(detected_img, caption='검출된 이미지', use_column_width=True)

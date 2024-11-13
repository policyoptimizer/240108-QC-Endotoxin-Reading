# 일단 돌아감!!

from flask import Flask, render_template, request, redirect, url_for, send_file
from ultralytics import YOLO
import os
import io
import zipfile
import uuid

app = Flask(__name__)

# 모델 경로 설정
model_path = r'D:\#.Secure Work Folder\BIG\Project\23~24Y\240108 QC Endotoxin Reading\240108 Endotoxin Reading_Rev.01.v2i.yolov8\runs\detect\train2\weights\best.pt'

# 모델 로드
try:
    model = YOLO(model_path)
    print("모델이 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"모델 로드 중 오류 발생: {e}")
    model = None

# 결과 폴더 설정
RESULT_FOLDER = 'static/results'
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# 폴더 생성
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        # 테스트 이미지 폴더 경로 설정
        images_folder = r'D:\#.Secure Work Folder\BIG\Project\23~24Y\240108 QC Endotoxin Reading\240108 Endotoxin Reading_Rev.01.v2i.yolov8\test\images'

        if not os.path.exists(images_folder):
            return "이미지 폴더가 존재하지 않습니다.", 400

        images = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        if not images:
            return "이미지가 없습니다.", 400

        # 고유한 결과 폴더 생성
        unique_id = str(uuid.uuid4())
        run_result_folder = os.path.join(app.config['RESULT_FOLDER'], unique_id)
        os.makedirs(run_result_folder, exist_ok=True)

        results = []
        for img_name in images:
            img_path = os.path.join(images_folder, img_name)

            try:
                # YOLOv8 모델로 예측 수행
                prediction = model.predict(source=img_path, save=True, project=run_result_folder, name='.', exist_ok=True)

                # 결과 이미지 경로
                result_image_path = os.path.join(run_result_folder, img_name)
                if not os.path.exists(result_image_path):
                    results.append({
                        'original_image': img_name,
                        'error': "결과 이미지를 생성하지 못했습니다."
                    })
                    continue

                result_image_url = url_for('static', filename=f'results/{unique_id}/' + img_name)

                results.append({
                    'original_image': img_name,
                    'result_image': result_image_url
                })
            except Exception as e:
                results.append({
                    'original_image': img_name,
                    'error': f"이미지 처리 중 오류 발생: {e}"
                })

        return render_template('result.html', results=results, unique_id=unique_id)
    else:
        return redirect(url_for('index'))

@app.route('/download_all/<unique_id>')
def download_all(unique_id):
    run_result_folder = os.path.join(app.config['RESULT_FOLDER'], unique_id)
    if not os.path.exists(run_result_folder):
        return "다운로드할 결과가 없습니다.", 400

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in os.listdir(run_result_folder):
            file_path = os.path.join(run_result_folder, filename)
            zf.write(file_path, arcname=filename)
    memory_file.seek(0)
    return send_file(memory_file, download_name='results.zip', as_attachment=True)

if __name__ == '__main__':
    if model is not None:
        app.run(debug=True)
    else:
        print("모델이 로드되지 않았으므로 서버를 시작하지 않습니다.")

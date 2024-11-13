# 보고서 측면에서 좀 더 개선됨

from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
from ultralytics import YOLO
import os
import io
import zipfile
import uuid
from datetime import datetime
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')  # Matplotlib 백엔드를 'Agg'로 설정
import matplotlib.pyplot as plt
from collections import Counter

app = Flask(__name__)

app.secret_key = '0000'  # 테스트용 secret key 설정

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
        # 배치번호 가져오기
        batch_number = request.form.get('batch_number')
        if not batch_number:
            flash('배치번호를 입력하세요.')
            return redirect(url_for('index'))

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

        report_data = {
            'batch_number': batch_number,
            'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_images': len(images),
            'image_results': []
        }

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

                # 검출된 객체 수 계산
                num_objects = len(prediction[0].boxes)

                results.append({
                    'original_image': img_name,
                    'result_image': result_image_url,
                    'num_objects': num_objects
                })

                # 보고서 데이터에 추가
                report_data['image_results'].append({
                    'image_name': img_name,
                    'num_objects': num_objects
                })
            except Exception as e:
                results.append({
                    'original_image': img_name,
                    'error': f"이미지 처리 중 오류 발생: {e}"
                })

        # 객체 수에 따른 이미지 수 계산
        counts = [img_result['num_objects'] for img_result in report_data['image_results']]
        count_distribution = Counter(counts)

        # 그래프 생성
        fig, ax = plt.subplots()
        ax.bar(count_distribution.keys(), count_distribution.values())
        ax.set_xlabel('Detected Objects')
        ax.set_ylabel('Number of Images')
        ax.set_title('Distribution of Detected Objects per Image')

        # 그래프를 이미지로 저장
        graph_image_path = os.path.join(run_result_folder, 'graph.png')
        plt.savefig(graph_image_path)
        plt.close()

        # 세션에 보고서 데이터 저장
        session['report_data'] = report_data

        return render_template('report.html', report_data=report_data, unique_id=unique_id)
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

@app.route('/download_report/<unique_id>')
def download_report(unique_id):
    report_data = session.get('report_data')
    if not report_data:
        return "보고서 데이터가 없습니다.", 400

    # 그래프 이미지 경로
    graph_image_path = os.path.join(app.config['RESULT_FOLDER'], unique_id, 'graph.png')

    # PDF 생성
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 보고서 제목
    pdf.cell(200, 10, txt="Endotoxin Detection Report", ln=True, align='C')

    # 배치번호 추가
    pdf.cell(200, 10, txt=f"Batch Number: {report_data['batch_number']}", ln=True, align='L')

    # 테스트 일자 및 총 이미지 수
    pdf.cell(200, 10, txt=f"Test Date: {report_data['test_date']}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Total Images: {report_data['total_images']}", ln=True, align='L')
    pdf.ln(10)

    # 그래프 이미지 추가
    pdf.image(graph_image_path, x=10, y=50, w=pdf.w - 20)
    pdf.ln(80)  # 그래프 아래에 여백 추가

    # 각 이미지별 결과
    pdf.ln(10)
    for idx, img_result in enumerate(report_data['image_results'], 1):
        pdf.cell(200, 10, txt=f"{idx}. {img_result['image_name']} - Detected Objects: {img_result['num_objects']}", ln=True, align='L')

    # PDF를 메모리에 저장
    pdf_output = pdf.output(dest='S').encode('latin1')

    return send_file(
        io.BytesIO(pdf_output),
        download_name='report.pdf',
        as_attachment=True,
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    if model is not None:
        app.run(debug=True)
    else:
        print("모델이 로드되지 않았으므로 서버를 시작하지 않습니다.")

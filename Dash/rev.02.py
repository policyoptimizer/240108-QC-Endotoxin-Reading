import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
import torch
import cv2
import numpy as np
from PIL import Image
import dataiku
from dataiku import Folder

# 데이터이쿠 폴더 설정
input_folder = dataiku.Folder("input")
best_folder = dataiku.Folder("best")
output_folder = dataiku.Folder("output")
test_img_folder = dataiku.Folder("test_img")

# 각 폴더의 경로 얻기
input_folder_path = input_folder.get_path()
best_folder_path = best_folder.get_path()
output_folder_path = output_folder.get_path()
test_img_folder_path = test_img_folder.get_path()

# 모델 파일 경로 설정 (best 폴더 내)
model_path = f"{best_folder_path}/best.pt"

# 모델 로드
model = torch.load(model_path, map_location=torch.device('cpu'))
model.eval()

def predict(image_path):
    image = Image.open(image_path).convert('RGB')
    image = np.array(image)
    image = cv2.resize(image, (640, 640))  # 모델 입력 크기에 맞게 조정
    image = torch.from_numpy(image).float().unsqueeze(0)  # 배치 차원 추가
    with torch.no_grad():
        output = model(image)
    return output

# Dash 앱 설정
# app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-image-upload')
])

def parse_contents(contents):
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    image_path = f"{input_folder_path}/temp_image.jpg"
    with open(image_path, "wb") as fh:
        fh.write(decoded)
    prediction = predict(image_path)
    return html.Div([
        html.H5("Prediction:"),
        html.Pre(str(prediction))
    ])

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')])
def update_output(contents):
    if contents is not None:
        children = parse_contents(contents)
        return children

if __name__ == '__main__':
    app.run_server(debug=True)


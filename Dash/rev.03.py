# 단순 이미지 업로드 기능까지

# 사용자가 이미지를 업로드하여 input 폴더에 저장하고, 
# 해당 이미지들을 객체 검출한 후 output 폴더에 저장하는 기능 추가되어야 함

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
import os

# Dash 앱 초기화
# app = dash.Dash(__name__)

# 업로드된 이미지를 저장할 로컬 디렉토리 설정
UPLOAD_DIRECTORY = "uploaded_images"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# 이미지 저장 함수
def save_image(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    with open(file_path, 'wb') as f:
        f.write(decoded)
    return file_path

# Dash 앱 레이아웃
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
        multiple=True
    ),
    html.Div(id='output-image-upload')
])

@app.callback(
    Output('output-image-upload', 'children'),
    [Input('upload-image', 'contents'),
     Input('upload-image', 'filename')]
)
def update_output(contents, filenames):
    if contents is not None:
        children = []
        for content, filename in zip(contents, filenames):
            file_path = save_image(content, filename)
            children.append(html.Div([
                html.H5(filename),
                html.Img(src=content, style={'height':'50%', 'width':'50%'})
            ]))
        return children
    return html.Div([
        html.H5("No image uploaded.")
    ])

if __name__ == '__main__':
    app.run_server(debug=True)


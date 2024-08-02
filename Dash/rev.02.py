# 일단 이미지를 업로드해서 화면에 보여지는 것부터

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
from PIL import Image
from io import BytesIO
import dataiku

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

@app.callback(
    Output('output-image-upload', 'children'),
    [Input('upload-image', 'contents')]
)
def update_output(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        image = Image.open(BytesIO(decoded))
        image.show()  # 사용자가 업로드한 이미지를 표시합니다.
        return html.Div([
            html.Img(src=contents, style={'height':'50%', 'width':'50%'})
        ])
    return html.Div([
        html.H5("No image uploaded.")
    ])

#if __name__ == '__main__':
#    app.run_server(debug=True)


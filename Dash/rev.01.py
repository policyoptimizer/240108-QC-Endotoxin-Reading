# 가장 초기 모델
# 구색만 갖췄음

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64

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
    with open("temp_image.jpg", "wb") as fh:
        fh.write(decoded)
    prediction = predict("temp_image.jpg")
    return html.Div([
        html.H5("Prediction:"),
        html.Pre(prediction)
    ])

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')])
def update_output(contents):
    if contents is not None:
        children = parse_contents(contents)
        return children

if __name__ == '__main__':
    app.run_server(debug=True)



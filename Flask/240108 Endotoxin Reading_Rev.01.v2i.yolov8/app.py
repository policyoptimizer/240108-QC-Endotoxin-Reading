from flask import Flask, render_template, request
import torch
from PIL import Image
import os
from torchvision import transforms

app = Flask(__name__)

# 모델 로드
model = torch.load('runs/detect/train2/weights/best.pt')
# model.eval()

# 이미지 전처리 함수
def transform_image(image_path):
   image = Image.open(image_path)
   return transforms.ToTensor()(image)

@app.route('/', methods=['GET'])
def index():
   return render_template('index.html')

@app.route('/detect', methods=['GET', 'POST'])
def detect():
   if request.method == 'POST':
       images_folder = 'test'
       images = os.listdir(images_folder)
       results = []
       for img_name in images:
           img_path = os.path.join(images_folder, img_name)
           img_tensor = transform_image(img_path)
           with torch.no_grad():
               prediction = model(img_tensor)
           results.append((img_name, prediction.xyxy[0].tolist()))
       return render_template('result.html', results=results)
   else:
       return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True)

import io
import json
from flask import Flask, render_template, request, url_for
from flask import jsonify
from flask_cors import CORS
# from connection import get_connection, get_s3_connection
#import base64
#import cv2
import joblib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

import requests
from PIL import Image
from io import BytesIO
import time

init_Base64 = 21
label_dict = {0:'가지', 1:'계란', 2:'고등어', 3:'당근', 4:'베이글', 5:'새우', 6:'양파', 7:'오징어', 8:'토마토', 9:'파프리카', 10:'피망'}

IMAGE_HEIGHT = 64
IMAGE_WIDTH = 64
IMAGE_CHANNELS = 3

app = Flask(__name__)
cors = CORS(app, resources={r"/camera/*": {"origins": "*"}})


@app.route('/camera')
def index():
    return render_template('index.html')

@app.route('/camera/predict', methods=['post']) # 'get'
def make_prediction():
    # s3_connection = get_s3_connection()
    image_file = request.files['image'] # file로 보내기

    #default_value = '0'
    #image_file = request.form.get(r'image', default_value)
    #image_file = request.form['image']
    print(image_file)
    #print(request.files)

    # uri = request.args.get('img_url')

    # img url로 받기
    # url = "https://img.hankyung.com/photo/202012/99.24812305.1.jpg"
    #url = request.args['img_url']
    #start = time.time()
    #res = requests.get(url)
    # print(url)
    # print(res)
    #print(time.time() - start)

    #image_file = BytesIO(res.content)

    if not image_file:
        #return render_template('index.html', label="no files")
        return jsonify({
            "label": 'error',
        })

    pil_img = Image.open(image_file)

    pil_img = pil_img.resize((IMAGE_HEIGHT, IMAGE_WIDTH), Image.BILINEAR)
    pil_img = np.array(pil_img)

    if len(pil_img.shape) == 2:  # Black and white
        pil_img = pil_img.reshape((1, IMAGE_HEIGHT, IMAGE_WIDTH, 1))
        pil_img = np.repeat(pil_img, 3, axis=3)

    pil_img = pil_img.reshape((1, IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANNELS))
    pil_img = tf.cast(pil_img, tf.float32) ## 추가

    y_predict = model.predict(pil_img)
    # print(y_predict)

    label = label_dict[y_predict[0].argmax()]
    index = str(np.squeeze(y_predict)) # 위치확인
    print(index)
    confidence = y_predict[0][y_predict[0].argmax()]
    lb = '{} {:.2f}%'.format(label, confidence * 100)

    json_obj = {
            "label" : label,
            "probability": lb
            }

    print(json_obj)
    # return render_template('index.html', label=lb)
    return jsonify({
        "label": label,
        "probability": lb
        })
#{
#            'statusCode': 200,
#            'headers': {
#                'Access-Control-Allow-Headers': '*',
#                'Access-Control-Allow-Origin': '*',
#                'Access-Control-Allow-Methods': '*'
#                },
#            'body': json.dumps(json_obj)
#            }


if __name__ == '__main__':
    model = load_model("food_classifer.h5")
    if model:
        print('model load success')

    app.run(port=5000, debug=False, host='0.0.0.0') # host='0.0.0.0' => 외부에서 접근 가능


#### model load 못해서 predict가 안됨. => h5파일 저장해서 해결


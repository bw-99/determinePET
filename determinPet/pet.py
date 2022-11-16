import os
from sqlite3 import Timestamp
import urllib
import numpy as np
import time
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from imageai.Detection.Custom import (CustomObjectDetection,
                                      DetectionModelTrainer)
import json
import requests
from base64 import b64decode
import webbrowser

from send_kakao import get_access_token, get_token, kakao_init, send_kakaotalk

PRE_TRAINED_MODEL = "detection_model-ex-006--loss-0014.752.h5"
ACCESS_TOKEN = ""

def train_model():
    trainer = DetectionModelTrainer()
    trainer.setModelTypeAsYOLOv3()
    trainer.setDataDirectory(data_directory="./petDataSet")
    trainer.setTrainConfig(
        object_names_array=['pet'],
        batch_size=2,
        num_experiments=30,
        train_from_pretrained_model=f"./models/{PRE_TRAINED_MODEL}",
        )
        
    trainer.trainModel()

def evaluate_model():
    trainer = DetectionModelTrainer()
    trainer.setModelTypeAsYOLOv3()
    trainer.setDataDirectory(data_directory="output")

    metrics = trainer.evaluateModel(
        model_path="drive/MyDrive/output/models", 
        json_path="drive/MyDrive/output/json/detection_config.json",               
        iou_threshold=0.5, 
        object_threshold=0.3, 
        nms_threshold=0.5
        )

    return metrics.pop()["model_file"].split("\\")[-1]

def detect_object_memory(model_route):
    filename = take_photo()

def detect_object_file(input_image,model_route):
    detector = CustomObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(f"{model_route}")
    detector.setJsonPath(f"drive/MyDrive/output/json/detection_config.json")
    detector.loadModel()
    returned_image = detector.detectObjectsFromImage(
        input_image=input_image,
        output_image_path=f"drive/MyDrive/output/detection/{input_image}_detection.jpg",
        output_type="file", 
        minimum_percentage_probability=50,
        input_type="file",
        )

# 메인 함수
def realtime_detecting(IP_ADDRESS, model_route):
    print(model_route)
    detector = CustomObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(f"./petDataSet/models/{model_route}")
    detector.setJsonPath(f"./petDataSet/json/detection_config.json")
    detector.loadModel()
    cap = cv2.VideoCapture(IP_ADDRESS)
    count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            output_name = "./images/output/%06d.jpg" % count
            output, detections = detector.detectObjectsFromImage(
                input_image=frame,
                output_image_path=output_name,
                output_type="array", 
                minimum_percentage_probability=60,
                input_type="array",
            )

            for detect in detections:
                frame = cv2.rectangle(frame, detect['box_points'][0:2],detect['box_points'][2:4], color = (0,255,0), thickness= 3)
                cv2.putText(frame,f"{detect['name']}\n{detect['percentage_probability']}%",detect['box_points'][2:4], cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)
                cv2.imwrite(f'{Timestamp.microsecond}.jpg',frame)
                send_kakaotalk(ACCESS_TOKEN)

            cv2.imshow("resize img", frame)
        else:
            print(ret)
            break
        count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break



# def send_kakaotalk() :
#     url="https://kapi.kakao.com/v2/api/talk/memo/default/send"
#     # kapi.kakao.com/v2/api/talk/memo/default/send 

#     print("Bearer" + ACCESS_TOKEN)

#     headers={
#         "Authorization" : "Bearer " + ACCESS_TOKEN,
#         "Content-Type" : "application/x-www-form-urlencoded"
#     }


#     data= {
#         "template_object":  json.dumps({
#         	"object_type": "text",
#             "text": "test",
#             "link": {
#                 "web_url" : "lorem ipsum",
#                 "mobile_web_url" : "lorem ipsum"
#             },
#             "button_title" : "lorem ipsum"
#         })
#     }

#     response = requests.post(url, headers=headers, data=data)
#     print(response.content)

    

if __name__ == "__main__":
    try:
        ACCESS_TOKEN = kakao_init()
        option = eval(input("모델 훈련 : 1,\n모델 선정 후 검출: 2,\n사진 검출 : 3,\n실시간 검출 : 4\n"))
    
        best_model = None

        if(option == 1):
            # # # 캐시 삭제
            # # dir_cache = "drive/MyDrive/output/cache"
            # # for f in os.listdir(dir_cache):
            # #     os.remove(os.path.join(dir_cache, f))

            # dir_model = "./models"
            # # dir_model = "drive/MyDrive/output/models"
            # for f in os.listdir(dir_model):
            #     if(f != PRE_TRAINED_MODEL and f != "pretrained-yolov3.h5"):
            #         os.remove(os.path.join(dir_model, f))

            # 모델 훈련
            train_model()
        elif(option == 2):
            # 최고 모델 검출
            best_model = evaluate_model()
            print(best_model)

        else:
            best_model = "detection_model-ex-029--loss-0020.484.h5"
            model_route = f"drive/MyDrive/output/models/{best_model}"
            if(option == 3):
                input_image = input("입력 이미지 : ")
                # 사진 검출
                detect_object_file(f"drive/MyDrive/output/{input_image}",model_route)
            else:
                # 실시간 검출
                # IP_ADDRESS = input("ip주소 : ") + "/video"
                IP_ADDRESS = "http://192.168.219.103:8080/video"
                realtime_detecting(IP_ADDRESS, PRE_TRAINED_MODEL)
                # detect_object_memory(model_route)
    except Exception as err:
        # Errors will be thrown if the user does not have a webcam or if they do not
        # grant the page permission to access it.
        print(str(err))




# API_KEY = "1dcc5cb6841f71bbdf5438b9e73efcc7"
# ACCESS_TOKEN = "I0VNayCVusT0o8serV4KIpkqGEqFQEcbpGDaczhJJcesQyrUnSoJMwzeQ2V1ZmSreBgE3wo9cxgAAAGEdY6rGA"

# url="https://kapi.kakao.com/v2/api/talk/memo/default/send"

# # kapi.kakao.com/v2/api/talk/memo/default/send 

# print("Bearer" + ACCESS_TOKEN)

# headers={
#     "Authorization" : "Bearer " + ACCESS_TOKEN,
#     "Content-Type" : "application/x-www-form-urlencoded"
# }


# data= {
#     "template_object":  json.dumps({
#     	"object_type": "text",
#         "text": "test",
#         "link": {
#             "web_url" : "lorem ipsum",
#             "mobile_web_url" : "lorem ipsum"
#         },
#         "button_title" : "lorem ipsum"
#     })
# }

# response = requests.post(url, headers=headers, data=data)
# print(response.content)

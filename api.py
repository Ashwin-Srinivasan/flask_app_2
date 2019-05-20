import http.client, urllib.request, urllib.parse, urllib.error, base64, json, cv2
from urllib.request import urlopen
from PIL import Image
import numpy as np
import requests
import cv2
import os


def call(image_paths):

    subscription_key = "8be1f69d512f46b29d6e696c72742295"
    vision_base_url = "https://eastus.api.cognitive.microsoft.com/vision/v2.0/"

    analyze_url = vision_base_url + "analyze"

    vision_dict = {}

    for image_path in image_paths:
        #print(image_path)
        image_data = open(image_path, "rb").read()
        headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
                      'Content-Type': 'application/octet-stream'}
        params     = {'visualFeatures': 'Categories, Description, Color, Objects, Tags'}
        #print(analyze_url)
        #print(image_data)
        response = requests.post(
            analyze_url, headers=headers, params=params, data=image_data)
        #print(response)
        response.raise_for_status()

        # The 'analysis' object contains various fields that describe the image. The most
        # relevant caption for the image is obtained from the 'description' property.
        analysis = response.json()

        vision_dict[image_path] = analysis


    #print(vision_data)



    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '501a6e80c2a74fc5b48fd0061c25b0a6',
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'true',
        'returnFaceAttributes': 'age,gender,smile,facialHair,headPose,glasses,emotion,hair,makeup,accessories,blur,exposure,noise'

    })

    faceIds = []
    faceDict = {}
#don't save the file. Pass the file on to the other function. 
    try:
        j = 0
        for image_path in image_paths:
            img = cv2.imread(image_path, 1)
            conn = http.client.HTTPSConnection('eastus.api.cognitive.microsoft.com')
            image_data = open(image_path, "rb").read()
            conn.request("POST", "/face/v1.0/detect?%s" % params, headers = headers, body = image_data)
            response = conn.getresponse()
            data = response.read()
            #print(data)
            my_json = data.decode('utf8').replace("'", '"')
            #print(my_json)
            pythonList = json.loads(my_json)
            faceDict[image_path] = []

            for i in range(len(pythonList)):
                faceIds.append(pythonList[i]['faceId'])
                left = pythonList[i]['faceRectangle']['left']
                top = pythonList[i]['faceRectangle']['top']
                right = left + pythonList[i]['faceRectangle']['width']
                bottom = top + pythonList[i]['faceRectangle']['height']
                cv2.rectangle(img, (left, top), (right, bottom), (125, 255, 51), 2)
                crop_img = img[top:bottom, left:right].copy()
                crop_img = cv2.resize(crop_img, (500, 500))
                cv2.imwrite(os.path.join('static' , pythonList[i]['faceId']+'.png'), crop_img)
                faceDict[image_path].append(pythonList[i])
                for k in range(i):
                    left2 = faceDict[image_path][k]['faceRectangle']['left']
                    top2 = faceDict[image_path][k]['faceRectangle']['top']
                    right2 = left2 + faceDict[image_path][k]['faceRectangle']['width']
                    bottom2 = top2 + faceDict[image_path][k]['faceRectangle']['height']
                    crop_img_2 = img[top2:bottom2, left2:right2].copy()
                    crop_img_2 = cv2.resize(crop_img_2, (500,500))
                    combo = np.concatenate((crop_img, crop_img_2), axis=1)
                    cv2.imwrite(os.path.join('static' , pythonList[i]['faceId']+'_'+faceDict[image_path][k]['faceId']+'.png'), combo)                    

            conn.close()
            #print("test_"+str(j))
            cv2.imwrite('test_'+str(j)+'.png',img)
            j += 1

    except Exception as e:
        #print(pythonList)
        print(e)
        print("[Errno {0}] {1}".format(e.errno, e.strerror)) 


    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '501a6e80c2a74fc5b48fd0061c25b0a6',
    }

    params = urllib.parse.urlencode({
        # Request parameters

    })

    #print(faceIds)
    if len(faceIds) > 1:
        try:
            conn = http.client.HTTPSConnection('eastus.api.cognitive.microsoft.com')
            body = json.dumps({'faceIds': faceIds})
            conn.request("POST", "/face/v1.0/group?%s" % params, headers = headers, body = body)
            response = conn.getresponse()
            data = response.read()
            #print(len(faceIds))
            #print(data)
            my_json = data.decode('utf8').replace("'", '"')
            #print(type(my_json))
            pythonList = json.loads(my_json)
            #print(type(pythonList))
            groups = pythonList['groups']
            for i in range(len(groups)):
                group = groups[i]
                directory = 'group_'+str(i)
                try:
                    os.mkdir(directory)
                except OSError:
                    pass 
                for face_id in group:
                    file = face_id + '.png'
                    os.rename(file, directory+'/'+file)
            messy = pythonList['messyGroup']
            directory = 'messyGroup'
            try:
                os.mkdir(directory)
            except OSError:
                pass 
            for face_id in messy:
                file = face_id + '.png'
                os.rename(file, directory+'/'+file)   

            conn.close()
        except Exception as e:
            #print('here')
            print("[Errno {0}] {1}".format(e.errno, e.strerror)) 
    dictionary = {'Vision': vision_dict, 'Faces': faceDict, 'Groupings': pythonList}
    with open("data_file.json", "w") as write_file:
        json.dump(dictionary, write_file, indent=4, sort_keys = True)

    return {'Vision': json.dumps(vision_dict, indent=4, sort_keys=True), 'Faces': json.dumps(faceDict, indent=4, sort_keys=True), 'Groupings': json.dumps(pythonList, indent=4, sort_keys=True)}

#what should it output? Face + Vision output
#Output Vision + Face details + Face groupings (each grouping on a different page?)
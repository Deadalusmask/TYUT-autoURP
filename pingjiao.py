import os
import requests
import xlwt
import cv2
import numpy as np
from keras.models import *
from keras.layers import *
from bs4 import BeautifulSoup

s=requests.Session()

img_url = 'http://202.207.247.49/validateCodeAction.do?random=0.14450151472734962'
login_url = 'http://202.207.247.49/loginAction.do'
list_url = 'http://202.207.247.49/jxpgXsAction.do?oper=listWj'
pj_url = 'http://202.207.247.49/jxpgXsAction.do'
post_url = 'http://202.207.247.49/jxpgXsAction.do?oper=wjpg'
imgresponse = s.get(img_url, stream=True)
# print(s.cookies)
image = imgresponse.content
DstDir = os.getcwd()+"/"
print("保存验证码到："+DstDir+"code.jpg"+"\n")
try:
    with open(DstDir+"code.jpg" ,"wb") as jpg:
        jpg.write(image)
except IOError:
    print("IO Error\n")
finally:
    jpg.close

model = model_from_json(open('my_model_architecture.json').read())    
model.load_weights('my_model_weights.h5')   

model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy'])

img = cv2.imread("code.jpg")
s_id     = input("学号：")
password = input("密码：")
code     = model.predict(img)

formData={'zjh':s_id,'mm':password,'v_yzm':code}
Post=s.post(url=login_url,data=formData)

list_response = s.get(list_url, stream=True).content.decode('gbk')
soup=BeautifulSoup(list_response,'lxml')
content=soup.find_all('img',title='评估')
for data in content:
    msg =data['name'].split('#@')
    form_data1={'wjbm':msg[0],'bpr':msg[1],'bprm':msg[2],'wjmc':msg[3],'pgnrm':msg[4],'pgnr':msg[5],'oper':'wjShow','pageSize':20,'page':1,'currentPage':1,'pageNo':''}
    print(form_data1)
    Post_pj=s.post(url=pj_url,data=form_data1)
    form_data2={'wjbm':msg[0],
            'bpr':msg[1],
            'pgnr':msg[5],
            'oper':'wjpg',
            'zgpj':'老师上课认真，学习了很多'.encode('gbk'),
            '0000000045':'10_1',
            '0024' => '10_1',
            '0025' => '10_1',
            '0026' => '10_1',
            '0027' => '10_1',
            '0028' => '10_1',
            '0029' => '10_1',
            '0030' => '10_1',
            '0031' => '10_1',
            '0032' => '10_1',
            '0033' => '10_1',
            }
    Post_tj=s.post(url=pj_url,data=form_data2)
    print(Post_tj.status_code)

import os
import requests
import xlwt
from bs4 import BeautifulSoup
import numpy as np
import cv2
from keras.models import *
from keras.layers import *

s=requests.Session()

imgUrl='http://202.207.247.49/validateCodeAction.do?random=0.14450151472734962'
imgresponse = s.get(imgUrl, stream=True)
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

#识别验证码
img = cv2.imread("code.jpg")
model = model_from_json(open('my_model_architecture.json').read())    
model.load_weights('my_model_weights.h5')   
model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy'])
s_id = input("学号：")
password = input("密码：")
code = model.predict(img)

formData={'zjh':s_id,'mm':password,'v_yzm':code}
Post=s.post(url='http://202.207.247.49/loginAction.do',data=formData)
# print(Post.status_code)

#获取基本信息
detailURL='http://202.207.247.49/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2016-2017%D1%A7%C4%EA%C7%EF(%C1%BD%D1%A7%C6%DA)'
html=s.get(url=detailURL)
main=html.content.decode('gbk')
soup=BeautifulSoup(main,'lxml')
content=soup.find_all('td',align="center")
#将信息放入一个list中,创建new_list(方便后续存入excel)
data_list=[]
for data in content:
    data_list.append(data.text.strip())
new_list=[data_list[i:i+7] for i in range(0,len(data_list),7)]

#数据存入excel表格
book=xlwt.Workbook()
sheet1=book.add_sheet('sheet1',cell_overwrite_ok=True)
heads=[u'课程号',u'课序号',u'课程名',u'英文课程名',u'学分',u'课程属性',u'成绩']
ii=0
for head in heads:
    sheet1.write(0,ii,head)
    ii+=1
i=1
for list in new_list:
    j=0
    for data in list:
        sheet1.write(i,j,data)
        j+=1
    i+=1
book.save('Score.xls')
print('\n录入成功！')

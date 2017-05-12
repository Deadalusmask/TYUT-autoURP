from PIL import Image, ImageDraw, ImageFont, ImageFilter
import string
import random
import numpy as np
from keras.models import *
from keras.layers import *
from keras.utils import plot_model

characters = string.digits + string.ascii_uppercase + string.ascii_lowercase
width, height, n_len, n_class = 60, 20, 4, len(characters)
def rndChar():
    return  characters[random.randint(0, len(characters)-1)]
def rndColor():
    return (random.randint(120, 255), random.randint(120, 255), random.randint(120, 255))
def rndColor2():
    return (random.randint(32, 100), random.randint(32, 100), random.randint(32, 100))

def img_gen():
    image = Image.new('RGB', (width, height), (255, 255, 255))
    font = ImageFont.truetype('LSANS.TTF', 16)
    draw = ImageDraw.Draw(image)
    backcolor1 = rndColor()
    backcolor2 = rndColor()
    for i in range(width):
        for j in range(height):
            draw.point((i, j), fill=backcolor1)
    for x in range(500):
        draw.point((random.randint(0,59), random.randint(0,19)), fill=backcolor2)
    
    text = []
    for t in range(4):
        char = rndChar()
        text.append(char)
        draw.text((14 * t, 2), char, font=font, fill=rndColor2())
    #image.save('code_gen.jpg', 'jpeg')
    img = np.array(image)
    return img,text

def gen(batch_size=32):
    X = np.zeros((batch_size, height, width, 3), dtype=np.uint8)
    y = [np.zeros((batch_size, n_class), dtype=np.uint8) for i in range(n_len)]
    while True:
        for i in range(batch_size):
            res = img_gen()
            X[i] = res[0]
            text = res[1]
            for j, ch in enumerate(text):
                y[j][i, :] = 0
                y[j][i, characters.find(ch)] = 1
        yield X, y

def decode(y):
    y = np.argmax(np.array(y), axis=2)[:,0]
    return ''.join([characters[x] for x in y])

input_tensor = Input((height, width, 3))
x = input_tensor
# Block 1
x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv1')(x)
x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv2')(x)
x = MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(x)

# Block 2
x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv1')(x)
x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv2')(x)
x = MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(x)

# Block 3
x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv1')(x)
x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv2')(x)
x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv3')(x)
x = MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(x)

# Block 4
x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv1')(x)
x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv2')(x)
x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv3')(x)
x = MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(x)


x = Flatten()(x)
x = Dropout(0.25)(x)
x = [Dense(n_class, activation='softmax', name='c%d'%(i+1))(x) for i in range(4)]
model = Model(input=input_tensor, output=x)

# model = model_from_json(open('my_model_architecture.json').read())    
# model.load_weights('my_model_weights.h5')   

model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy'])

# plot_model(model, to_file='model.svg',show_shapes=True)

model.fit_generator(gen(), samples_per_epoch=51200, nb_epoch=5, 
                    nb_worker=2, pickle_safe=True, 
                    validation_data=gen(), nb_val_samples=1280)

model.save_weights('my_model_weights.h5')
json_string = model.to_json()
open('my_model_architecture.json','w').write(json_string)  

X, y = next(gen(1))
y_pred = model.predict(X)
print('predict: read:',decode(y),'pred:',decode(y_pred))

# -*- coding: utf-8 -*-
"""Image Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r3JmM7Upe5m5v0y_NEmPhXhYLAU5LFom

### Data Diri

- Nama : Kevin Winardi
- ID Dicoding : kevinwinardi
- Dataset : https://www.kaggle.com/datasets/mahmoudreda55/satellite-image-classification

## Import Module
"""

# Commented out IPython magic to ensure Python compatibility.
import os
from zipfile import ZipFile
import tensorflow as tf
import numpy as np
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from google.colab import files
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pathlib
# %matplotlib inline

"""### Mengekstrak Data"""

with ZipFile ("Dataset.zip", "r") as zip_ref :
  zip_ref.extractall()

"""### Augmentasi dan pemisahan data"""

data = "/content/data"
train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest',
                    validation_split=0.2)

"""### Generator"""

train_generator = train_datagen.flow_from_directory(
    data,
    target_size=(150,150),
    class_mode = "categorical",
    shuffle = True,
    subset = "training",
)

valid_generator = train_datagen.flow_from_directory(
    data,
    target_size=(150,150),
    class_mode = "categorical",
    shuffle = True,
    subset = "validation",
)

"""### Callback"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.85 and logs.get('val_accuracy')>0.85):
      print("\nNilai accuracy telah mencapai 85%!")
      self.model.stop_training = True
callbacks = myCallback()

"""### Model Sequential"""

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(16, (3,3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(200, activation = "relu"),
    tf.keras.layers.Dense(500, activation = "relu"),
    tf.keras.layers.Dense(4, activation = "softmax")
])
model.summary()

"""### Kompilasi Model"""

model.compile(loss = "categorical_crossentropy",
                 optimizer = "RMSprop",
                 metrics = ["accuracy"])

"""### Melatih Model"""

history = model.fit(
      train_generator,
      steps_per_epoch=25,
      epochs=50,
      validation_data=valid_generator,
      validation_steps=5,
      callbacks=[callbacks],
      verbose=2)

"""### Plot"""

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""### Percobaan"""

uploaded = files.upload()

for fn in uploaded.keys():
  path = fn
  img = image.load_img(path, target_size=(150,150))
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)
  print(fn)
  if classes[0][1]==1:
   print("Berawan")
  elif classes[0][2]==1:
    print("Gurun")
  elif classes[0][3]==1:
    print("Area hijau")
  else :
    print("Perairan")

"""### Tensorflow Lite"""

export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('imageClassification.tflite')
tflite_model_file.write_bytes(tflite_model)
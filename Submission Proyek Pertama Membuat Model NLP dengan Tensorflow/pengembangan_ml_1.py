# -*- coding: utf-8 -*-
"""Pengembangan_ML_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nYgRurRj3UbYrntIXdg9NeDu033LMOKO

# Biodata

- Nama : Kevin Winardi
- ID Dicoding : kevinwinardi
- Dataset : BBC News Archive (https://www.kaggle.com/datasets/hgultekin/bbcnewsarchive)

# Analisis dan memodifikasi data

### Mengimpor module
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
import re

"""### Mengubah file csv menjadi dataframe"""

df = pd.read_csv("bbc-news-data.csv" , sep ="\t")
df.head()

"""Tidak ada duplikat data dan semuanya bertipe object

### Membuang kolom yang tidak digunakan
"""

df = df.drop(columns = ["filename","title"])

"""### Mengecek info"""

df.info()

"""### One Hot Encoding"""

category = pd.get_dummies(df.category)
df = pd.concat([df,category],axis=1)
df = df.drop(columns = "category")
df.head(20)

"""# Machine Learning

## Callback
"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.9 and logs.get('val_accuracy')>0.9):
      print("\nAkurasi telah mencapai > 90%!")
      self.model.stop_training = True
callbacks = myCallback()

"""## Dataframe ke array numpy"""

content = df['content'].values
label = df[['business','entertainment','politics', 'sport','tech']].values

"""## Menghilangkan stopwords"""

def remove_stopwords(text):
  words = word_tokenize(text)
  filtered_words = [word for word in words if word.lower() not in stopwords.words('english')]
  return ''.join(filtered_words)
df['content']=df['content'].apply(remove_stopwords)

"""## Menghapus tanda baca"""

def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)
df['content'] = df['content'].apply(remove_punctuation)

"""## Membagi data latih dan data test"""

content_train,content_test, label_train,label_test = train_test_split(content,label,test_size = 0.2)

"""## Tokenizer"""

tokenizer = Tokenizer(num_words=5000, oov_token = "<oov>")
tokenizer.fit_on_texts(content_train)

"""## Padding dan sekuens"""

sequences_train = tokenizer.texts_to_sequences(content_train)
padded_train = pad_sequences(sequences_train)

sequences_test = tokenizer.texts_to_sequences(content_test)
padded_test = pad_sequences(sequences_test)

"""## Model"""

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=16),
    tf.keras.layers.LSTM(32),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(16,activation='relu'),
    tf.keras.layers.Dense(5, activation='softmax')
])
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])

"""## Melatih Model"""

history = model.fit(padded_train, label_train, epochs=25, validation_data=(padded_test, label_test), callbacks=[callbacks], validation_split=0.2)

"""## Plot loss dan akurasi"""

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
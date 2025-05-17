import json
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import random
import pickle

lemmatizer = WordNetLemmatizer() # Inisialisasi lemmatizer

words = []
classes = []
documents = []
ignore_words = ['?', '!', '.', ','] # Kata-kata yang diabaikan

# Muat data intents dari file JSON
with open('intents.json') as f:
    intents = json.load(f)

# Loop melalui setiap intent
for intent in intents['intents']:
    # Loop melalui setiap pola (pattern) dalam intent
    for pattern in intent['patterns']:
        # Tokenisasi: pecah kalimat menjadi kata-kata
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list) # Tambahkan kata-kata ke daftar 'words'
        # Tambahkan pasangan (daftar kata-kata, tag intent) ke daftar 'documents'
        documents.append((word_list, intent['tag']))
    # Tambahkan tag intent ke daftar 'classes' jika belum ada
    if intent['tag'] not in classes:
        classes.append(intent['tag'])

# Lemmatisasi dan bersihkan kata-kata
# Lemmatisasi: mengembalikan kata ke bentuk dasarnya (misal: 'running' -> 'run')
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
# Hapus duplikat dan urutkan kata-kata unik
words = sorted(list(set(words)))

# Hapus duplikat dan urutkan kelas/tag intent
classes = sorted(list(set(classes)))

print(len(documents), "documents")
print(len(classes), "classes", classes)
print(len(words), "unique lemmatized words", words)

# Simpan daftar kata-kata dan kelas/tag
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# --- Buat Data Training ---
training = []
output_empty = [0] * len(classes) # Vektor kosong untuk output (one-hot encoding)

# Loop melalui setiap dokumen (pasangan kata-kata & tag)
for doc in documents:
    bag = [] # Bag of words untuk dokumen saat ini
    pattern_words = doc[0] # Daftar kata-kata dalam pola
    # Lemmatisasi kata-kata dalam pola
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

    # Buat Bag of Words: 1 jika kata ada di pola, 0 jika tidak
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # Buat output row: 1 untuk tag intent yang sesuai (one-hot encoding)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1 # Set index tag intent menjadi 1

    training.append([bag, output_row]) # Tambahkan pasangan bag of words dan output row ke training data

# Acak data training
random.shuffle(training)
# Ubah menjadi array NumPy untuk training model
training = np.array(training, dtype=object) # Gunakan dtype=object agar tidak error dengan list di dalamnya

# Pisahkan fitur (X) dan label (y)
train_x = list(training[:,0]) # Bag of words (input)
train_y = list(training[:,1]) # One-hot encoding label (output)

print("Data training dibuat")


# --- Bangun Model Neural Network ---
# Model Sequential: layer-layer disusun secara berurutan
model = Sequential()
# Layer input dan hidden pertama: Jumlah neuron = 128, fungsi aktivasi ReLU
# Input shape: ukuran bag of words (jumlah kata unik)
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5)) # Dropout: membantu mencegah overfitting
# Layer hidden kedua: Jumlah neuron = 64, fungsi aktivasi ReLU
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
# Layer output: Jumlah neuron = jumlah kelas (tag intent), fungsi aktivasi softmax (untuk probabilitas)
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile model: Tentukan optimizer, loss function, dan metrik
# Optimizer Adam: algoritma populer untuk training
# Loss function: categorical_crossentropy cocok untuk klasifikasi multi-kelas
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# --- Latih Model ---
print("Mulai training model...")
# model.fit: Proses training
# train_x, train_y: Data training (input dan output)
# epochs: Berapa kali model melihat seluruh data training
# batch_size: Berapa banyak sampel yang diproses sebelum mengupdate bobot model
# verbose=1: Menampilkan progress training
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
print("Model berhasil ditrain")

# --- Simpan Model ---
# Simpan model yang sudah dilatih ke file (format HDF5)
model.save('chatbot_model.h5', hist)
print("Model disimpan sebagai chatbot_model.h5")
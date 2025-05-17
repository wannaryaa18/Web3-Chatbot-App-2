import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import random

lemmatizer = WordNetLemmatizer()

# Muat file-file yang sudah disimpan saat training
model = load_model('chatbot_model.h5')
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
intents = json.load(open('intents.json'))

# Fungsi untuk membersihkan kalimat input pengguna
def clean_up_sentence(sentence):
    # Tokenisasi: pecah kalimat menjadi kata-kata
    sentence_words = nltk.word_tokenize(sentence)
    # Lemmatisasi setiap kata
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Fungsi untuk membuat Bag of Words dari kalimat input pengguna
def bag_of_words(sentence, words, show_details=True):
    # Bersihkan kalimat
    sentence_words = clean_up_sentence(sentence)
    # Inisialisasi bag dengan 0 untuk setiap kata dalam vocabulary
    bag = [0]*len(words)
    # Buat bag of words: 1 jika kata dari input ada di vocabulary, 0 jika tidak
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1 # Set 1 jika kata ditemukan di vocabulary
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

# Fungsi untuk memprediksi kelas (intent) dari kalimat
def predict_class(sentence, model):
    # Buat Bag of Words
    p = bag_of_words(sentence, words, show_details=False)
    # Prediksi probabilitas menggunakan model
    # reshape(1, -1) untuk memastikan input berbentuk array 2D
    res = model.predict(np.array([p]))[0]
    # Tentukan threshold: minimal probabilitas untuk dianggap sebagai intent yang valid
    ERROR_THRESHOLD = 0.75 # Bisa disesuaikan
    # Ambil hasil prediksi di atas threshold
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # Urutkan berdasarkan probabilitas tertinggi
    results.sort(key=lambda x: x[1], reverse=True)
    # Buat list hasil (tag intent dan probabilitas)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# Fungsi untuk mendapatkan respons berdasarkan intent yang diprediksi
# Kita modifikasi sedikit agar bisa dipanggil dengan pesan langsung
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    result = "Maaf, saya tidak mengerti. Bisakah Anda mengatakannya dengan cara lain?" # Default fallback

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

# Fungsi baru yang akan dipanggil oleh aplikasi web/API
def get_chatbot_response(text):
    # Prediksi intent dari teks input
    intents_list = predict_class(text, model)

    # Jika ada intent yang terdeteksi di atas threshold
    if intents_list:
        # Dapatkan respons dari fungsi get_response
        response = get_response(intents_list, intents)
    else:
        # Jika tidak ada intent yang terdeteksi
        response = "Maaf, saya tidak mengerti. Bisakah Anda mengatakannya dengan cara lain?" # Fallback

    return response
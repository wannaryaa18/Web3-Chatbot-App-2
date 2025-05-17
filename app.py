from flask import Flask, request, jsonify, render_template
# Import fungsi chatbot Anda dari file chatbot.py
from chatbot import get_chatbot_response
import os # Import os untuk mengatur port saat deployment

app = Flask(__name__)

# Route untuk halaman utama
@app.route('/')
def index():
    # Render file index.html dari folder templates
    return render_template('index.html')

# Route API untuk mendapatkan respons chatbot dari input user
@app.route('/get_response', methods=['POST'])
def get_response_web():
    # Ambil data JSON dari permintaan (dari JavaScript)
    data = request.get_json()
    user_message = data.get('message') # Gunakan .get() agar aman jika kunci tidak ada

    if not user_message:
        return jsonify({'response': 'Mohon masukkan pesan.'}), 400 # Respons jika pesan kosong

    # Panggil fungsi chatbot Anda
    chatbot_response = get_chatbot_response(user_message)

    # Kembalikan respons dalam format JSON
    return jsonify({'response': chatbot_response})

# Jalankan aplikasi Flask
if __name__ == '__main__':
    # Saat lokal, debug=True
    # Saat deployment, gunakan host='0.0.0.0' dan port dari environment variable
    port = int(os.environ.get('PORT', 5000)) # Gunakan port 5000 sebagai default lokal
    app.run(debug=True, host='0.0.0.0', port=port)
FROM python:3.11-slim

# Set working directory di dalam kontainer
WORKDIR /app

# Copy file requirements.txt ke working directory
COPY requirements.txt .

# Instal library yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (punkt_tab)
RUN python -c "import nltk; nltk.download('punkt_tab', download_dir='/usr/share/nltk_data')"

# Download NLTK data (wordnet) <-- PASTIKAN BARIS INI ADA DI DOCKERFILE LOKAL ANDA
RUN python -c "import nltk; nltk.download('wordnet', download_dir='/usr/share/nltk_data')"

# Set NLTK_DATA environment variable
ENV NLTK_DATA=/usr/share/nltk_data

# Copy seluruh isi proyek ... (instruksi ini mungkin selanjutnya)
COPY . /app

# Hugging Face Spaces biasanya mengekspos aplikasi di port 7860
EXPOSE 7860

# Command untuk menjalankan aplikasi Flask Anda menggunakan Gunicorn
# Ganti 'app:app' jika instance Flask Anda di app.py bernama lain
# atau jika file utama Anda bukan app.py
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
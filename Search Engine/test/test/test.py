from flask import Flask, request, render_template
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Membaca dataset dari file Excel
df = pd.read_excel("indexdir/data_rumah.xlsx")  # Ganti dengan nama file dataset Anda

# Inisialisasi TF-IDF Vectorizer untuk kolom NAMA RUMAH
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df['NAMA RUMAH'])

def parse_price_conditions(query):
    """Mengambil rentang harga dari query."""
    prices = re.findall(r'\d+(?:\.\d{3})*(?:[\,]?\d{0,2})?', query)
    if len(prices) == 2:
        return (int(prices[0].replace('.', '').replace(',', '')), int(prices[1].replace('.', '').replace(',', '')))
    elif len(prices) == 1:
        return (int(prices[0].replace('.', '').replace(',', '')), None)
    return None

def build_combined_text(row):
    """Membangun teks gabungan dari kolom-kolom yang ada."""
    return f"{row['NAMA RUMAH']} {row['HARGA']} {row['KT']} {row['LB']} {row['LT']} {row['KM']} {row['GRS']}"

def filter_data(query):
    """Menyaring data berdasarkan kondisi dalam query."""
    filtered_df = df.copy()

    # Memeriksa kondisi harga
    price_conditions = parse_price_conditions(query)
    if price_conditions:
        min_price, max_price = price_conditions
        filtered_df = filtered_df[(filtered_df['HARGA'] >= min_price)]
        if max_price is not None:
            filtered_df = filtered_df[filtered_df['HARGA'] <= max_price]

    # Menghitung skor TF-IDF untuk kueri
    query_vector = tfidf_vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Menambahkan skor relevansi ke DataFrame berdasarkan NAMA RUMAH
    filtered_df['relevance_score'] = cosine_similarities
    filtered_df = filtered_df[filtered_df['relevance_score'] > 0]  # Hanya ambil yang relevan

    # Membangun teks gabungan untuk semua kolom
    filtered_df['combined_text'] = filtered_df.apply(build_combined_text, axis=1)

    # Menghitung skor TF-IDF untuk teks gabungan
    combined_tfidf_vectorizer = TfidfVectorizer()
    combined_tfidf_matrix = combined_tfidf_vectorizer.fit_transform(filtered_df['combined_text'])
    combined_query_vector = combined_tfidf_vectorizer.transform([query])
    combined_cosine_similarities = cosine_similarity(combined_query_vector, combined_tfidf_matrix).flatten()

    # Menambahkan skor relevansi untuk teks gabungan
    filtered_df['combined_relevance_score'] = combined_cosine_similarities
    filtered_df = filtered_df.sort_values(by=['combined_relevance_score', 'relevance_score'], ascending=False)

    return filtered_df[['NAMA RUMAH', 'HARGA', 'KT', 'LB', 'LT', 'KM', 'GRS', 'combined_relevance_score']]

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query_str = ""

    if request.method == 'POST':
        query_str = request.form['query']
        results = filter_data(query_str).to_dict(orient='records')

    return render_template('index.html', results=results, query=query_str)

if __name__ == '__main__':
    app.run(debug=True)

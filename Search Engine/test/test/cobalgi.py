import pandas as pd
from flask import Flask, request, render_template

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Paths to the Excel files
data_rumah_path = 'indexdir/data_rumah.xlsx'  # Sesuaikan jalur sesuai kebutuhan
harga_rumah_jaksel_path = 'indexdir/HARGA RUMAH JAKSEL.xlsx'  # Sesuaikan jalur sesuai kebutuhan

# Load the Excel files into DataFrames
data_rumah_df = pd.read_excel(data_rumah_path)
harga_rumah_jaksel_df = pd.read_excel(harga_rumah_jaksel_path)

# Check column names
print("data_rumah columns:", data_rumah_df.columns)
print("harga_rumah_jaksel columns:", harga_rumah_jaksel_df.columns)

# Clean column names
data_rumah_df.columns = data_rumah_df.columns.str.strip().str.lower()
harga_rumah_jaksel_df.columns = harga_rumah_jaksel_df.columns.str.strip().str.lower()

# Fill missing values
data_rumah_df.fillna('', inplace=True)
harga_rumah_jaksel_df.fillna('', inplace=True)

# Implement search function
def search(df, query):
    query = query.lower()
    query_terms = query.split()
    
    results = df
    for term in query_terms:
        results = results[results.apply(lambda row: row.astype(str).str.contains(term, case=False).any(), axis=1)]
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query_str = ""

    if request.method == 'POST':
        query_str = request.form['query']
        print("Query Received:", query_str)  # Debugging kueri yang diterima
        results_df = search(data_rumah_df, query_str)
        results = results_df.to_dict(orient='records')
        print("Search Results:", results)  # Debugging hasil pencarian

    return render_template('index.html', results=results, query=query_str)

if __name__ == '__main__':
    app.run(debug=True)

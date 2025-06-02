# 🚀 MLOps Titanic Survival Prediction

Proyek ini merupakan pipeline MLOps yang dibangun menggunakan **Jenkins** dan **Docker** untuk memproses data Titanic, melakukan pelatihan model machine learning, serta mendeploy model ke dalam container aplikasi.

## 📦 Struktur Proyek

```

├── Data/
│   ├── raw/
│   └── clean/
├── Model/
│   ├── model/
│   ├── metadata/
│   └── preprocessor/
├── Script/
│   ├── data\_preparation.py
│   ├── train\_model.py
│   └── deploy\_model.py
├── requirements.txt
├── Dockerfile
├── Jenkinsfile
└── README.md

````

## ⚙️ Pipeline Stages

1. **Checkout Repository**  
   Mengambil kode dari GitHub.

2. **Install Dependencies**  
   Membuat environment virtual Python dan menginstal dependencies.

3. **Data Preparation**  
   Membersihkan dan menyiapkan data dari folder `Data/raw` ke `Data/clean`.

4. **Train Model**  
   Melatih model machine learning dan menyimpan hasilnya ke folder `Model/model`.

5. **Deploy Model**  
   Menyimpan metadata dan mempersiapkan model untuk produksi.

6. **Build & Push Docker Image**  
   Membuat image Docker dan mendorongnya ke Docker Hub.

7. **Test Docker Image**  
   Menjalankan container sementara untuk memastikan image berjalan dengan benar.

8. **Deploy Application**  
   Mendeploy container final ke port lokal (`3000`).

## 📂 Contoh Perintah Manual

Jalankan di local environment:

```bash
# Setup
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

# Data Preparation
python Script/data_preparation.py \
    --data_dir Data/raw \
    --data_new Data/clean \
    --output_dir Model/preprocessor \
    --target_col Survived \
    --random_state 42 \
    --columns_to_remove Cabin PassengerId Name

# Train Model
python Script/train_model.py \
    --data_dir Data/clean \
    --model_dir Model/model \
    --model_name random_forest

# Deploy Model
python Script/deploy_model.py \
    --model_path Model/model/random_forest.pkl \
    --model_dir Model/model \
    --metadata_dir Model/metadata
````

## 🐳 Docker

Build dan jalankan aplikasi:

```bash
docker build -t mlops-local .
docker run -d -p 3000:3000 --name mlops-app mlops-local
```

## 🧪 Testing Endpoint

Setelah aplikasi berjalan, test endpoint:

```bash
curl http://localhost:3000/
```

## 📌 Teknologi

* Python 3.x
* Jenkins
* Docker
* Scikit-learn
* Pandas
* Flask (jika digunakan untuk deployment)

## 👩‍💻 Kontributor

* **Berlian Ishma Zhafira Sujana** – Machine Learning Engineer & DevOps Enthusiast
  [GitHub: berlianishma08](https://github.com/berlianishma08)

## 📄 Lisensi

Proyek ini berada di bawah lisensi MIT. Silakan gunakan dan modifikasi sesuai kebutuhan.

```

---

Kalau kamu ingin menambahkan badge CI/CD Jenkins, Docker Pulls, atau penjelasan detail tiap script Python, tinggal bilang saja ya!
```

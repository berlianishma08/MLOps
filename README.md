# 🚀 MLOps Titanic Survival Prediction

Proyek ini merupakan pipeline MLOps yang dibangun menggunakan **Jenkins** dan **Docker** untuk memproses data Titanic, melakukan pelatihan model machine learning, serta mendeploy model ke dalam container aplikasi.

## 📦 Struktur Proyek

```

MLOps/
├── .git/                    # Metadata Git (version control)
├── Data/                    # Folder data proyek ML
│   └── raw/                 # Data mentah (belum diproses)
├── Notebook/                # Notebook Jupyter untuk eksperimen & dokumentasi model
├── Script/                  # Script Python modular untuk pipeline ML
│   ├── data_preparation.py  # Script untuk preprocessing dan pembersihan data
│   ├── train_model.py       # Script untuk training model ML
│   └── deploy_model.py      # Script untuk menyimpan atau serving model
├── templates/               # Template HTML untuk Flask Web App
│   └── index.html           # Merender halaman web
├── jenkins/                 # Konfigurasi tambahan untuk Jenkins
├── myenv/                   # Virtual environment Python (hasil dari `python3 -m venv`)
├── app.py                   # Aplikasi utama berbasis Flask (Web API)
├── fix_model.py             # Fixing atau validasi model
├── Dockerfile               # Konfigurasi Docker untuk membuat image proyek
├── docker-compose.yml       # Menjalankan beberapa container sekaligus (Flask, Jenkins, dsb.)
├── Jenkinsfile              # Pipeline deklaratif untuk CI/CD menggunakan Jenkins
├── requirements.txt         # Dependencies Python (untuk `pip install -r`)
├── environment.yml          # Environment 
└── README.md                # Dokumentasi proyek (deskripsi, instruksi, teknologi, dll.)


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

---

## 📦 Deployment & Implementasi Proyek

### 🧰 Prasyarat Sistem

**Update Sistem & Instalasi Docker**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
```

**Konfigurasi Docker User (Opsional, agar tidak perlu `sudo`)**

```bash
sudo usermod -aG docker $USER
```

**Verifikasi Instalasi**

```bash
docker --version
docker-compose --version
```

---

### 🗂️ Persiapan Jenkins

**Buat Folder Persisten untuk Jenkins**

```bash
mkdir -p ./jenkins_home
sudo chown -R 1000:1000 ./jenkins_home
sudo chmod -R 755 ./jenkins_home
```

---

### 🚀 Menjalankan Aplikasi

**1. Hentikan Container Jenkins Lama (jika ada)**

```bash
docker rm -f [nama_container_jenkins]
```

**2. Jalankan Jenkins & Aplikasi**

```bash
docker-compose up -d
```

**3. Verifikasi Container**

```bash
docker ps
```

---

### 🌐 Akses Aplikasi

* **Jenkins Dashboard**: `http://<PUBLIC-IP-EC2>:8080`
* **Aplikasi MLOps (Flask)**: `http://<PUBLIC-IP-EC2>:3000`

---

### ⚙️ Setup Awal Jenkins

1. Akses Jenkins melalui browser.
2. Ikuti wizard untuk *unlock Jenkins*, *install plugin default*, dan *buat admin user*.

---

### 🔗 Integrasi GitHub dan Jenkins (CI/CD Webhook)

**Tambahkan GitHub Server di Jenkins**

1. Masuk ke: `Manage Jenkins → Configure System`
2. Scroll ke bagian **GitHub Servers** → klik **Add GitHub Server**
3. Centang opsi `Manage hooks`
4. Masukkan **Personal Access Token (PAT)** GitHub
5. Klik tombol `Test Connection`

**(Opsional) Setup Webhook Manual di GitHub Repo**

1. Masuk ke GitHub → `Settings → Webhooks → Add webhook`
2. Isi form berikut:

   * **Payload URL**: `http://<PUBLIC-IP-EC2>:8080/github-webhook/`
   * **Content type**: `application/json`
   * **Events**: `Just the push event`
3. Klik **Add webhook**

---

### 🔄 Workflow CI/CD

* Setiap **push** ke branch yang dikonfigurasi akan **otomatis trigger pipeline** di Jenkins.
* Pipeline akan mengikuti instruksi pada `Jenkinsfile`.
* Pantau status pipeline di **Jenkins Dashboard**.
* Jika pipeline tidak berjalan:

  * Cek log di Jenkins
  * Cek webhook delivery status di GitHub (`Settings → Webhooks → Recent Deliveries`)

---

## 🧪 Testing Endpoint

Setelah aplikasi berjalan, test endpoint:

```bash
curl http://localhost:3000/
```

## 📌 Teknologi

* Python 3.12
* Jenkins
* Docker
* Scikit-learn
* Pandas
* Flask

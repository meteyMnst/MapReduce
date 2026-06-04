# 🔴🔵 Bordo Mavi Bulut Arama Motoru

Tamamen **Serverless (Sunucusuz)** mimari üzerine inşa edilmiş, yüksek performanslı ve otomatik ölçeklenebilir bir arama motoru projesi. Bu proje, devasa boyutlardaki metin verilerini hızlı bir şekilde endeksleyip arama yapılabilmesini sağlamak amacıyla Google'ın temelini oluşturan **MapReduce** konseptinin modern AWS bulut servisleriyle uygulanmış halidir.

---

## 🎯 Temel Özellikler

* **%100 Sunucusuz Mimari:** Geleneksel sunucu yönetimi yoktur, sadece işlem yapıldığında çalışan ve maliyet çıkaran bir yapı (Pay-as-you-go) kullanılmıştır.
* **Olay Güdümlü (Event-Driven) Çalışma:** S3'e yüklenen her yeni veri, anında kendi Lambda fonksiyonunu tetikleyerek eşzamanlı (concurrent) işlem gücü sağlar.
* **TF-IDF Algoritması:** Arama sonuçları, metin madenciliği standartlarına uygun olarak TF-IDF (Term Frequency-Inverse Document Frequency) skorlamasına göre sıralanır.
* **Otomatik Altyapı Kurulumu:** Tüm AWS kaynakları (IAM, S3, Lambda, API Gateway) tek bir PowerShell betiği ile saniyeler içinde ayağa kaldırılır.

---

## ☁️ AWS Mimarisindeki Bileşenler

Sistem aşağıdaki Amazon Web Services (AWS) teknolojileri üzerinde çalışmaktadır:

* **AWS S3 (Simple Storage Service):** Projenin ana veri merkezidir. Hem ham verileri (Raw Data) hem Inverted Index dosyalarını güvenle depolar. Ayrıca Trabzonspor temalı statik Frontend arayüzünü (Web Hosting) barındırır.
* **AWS Lambda:** Sistemin işlem gücüdür. Verileri parçalayan (Mapper), kelime frekanslarını birleştirip hesaplayan (Reducer) ve API'den gelen arama sorgularını anlık olarak işleyen (Search) fonksiyonları barındırır.
* **AWS API Gateway:** Kullanıcının web arayüzünden yaptığı arama sorgularını karşılayıp güvenli bir REST API formatında Search Lambda fonksiyonuna ileten köprü görevini üstlenir.

---

## 🔄 Veri Akışı ve MapReduce Süreci

### 1. Veri Toplama ve Depolama
Veriler, `fetch_fast.py` betiği aracılığıyla **Wikipedia API** üzerinden canlı ve rastgele makaleler çekilerek elde edilir. Çekilen makalelerin başlık, URL ve içerik metinleri tekil `.json` dosyalarına dönüştürülerek AWS S3 bucket'ına (raw-pages) aktarılır.

### 2. Map (Parçalama) Evresi
S3'e yeni bir ham makale dosyası eklendiği anda **Mapper** Lambda fonksiyonu otomatik olarak tetiklenir. Metni kelimelere böler, gereksiz karakterleri temizler, frekanslarını sayar ve sonuçları `map-output/` klasörüne kaydeder. Sisteme 500 dosya yüklenirse, 500 adet Mapper fonksiyonu eşzamanlı olarak devreye girer.

### 3. Reduce (Birleştirme ve Endeksleme) Evresi
**Reducer** fonksiyonu, parçalanmış map verilerini toplar. TF-IDF skorlamalarını hesaplayarak arama motorunun bel kemiği olan devasa ana sözlüğü (`inverted_index.json`) oluşturur ve bunu tekrar S3 üzerinde konumlandırır.

---

## 📂 Proje Yapısı

Sistemin klasör hiyerarşisi aşağıdaki gibidir:

```text
MapReduce/
├── arama-motoru/
│   ├── scripts/
│   │   ├── mapper.py        # Metin parçalama ve frekans hesabı
│   │   ├── reducer.py       # Verileri birleştirme ve TF-IDF skorlaması
│   │   └── search.py        # API Gateway üzerinden gelen sorguları işleme
│   └── index.html           # Trabzonspor temalı, S3'te barındırılan arama arayüzü
├── veri-toplama/
│   └── fetch_fast.py        # Wikipedia'dan rastgele makale çeken script
└── aws_setup.ps1            # AWS altyapısını otomatik kuran deployment betiği
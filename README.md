# Bordo Mavi Bulut Arama Motoru 🔴🔵

## 🎯 Proje Amacı
Bu proje, devasa boyutlardaki metin verilerini hızlı bir şekilde endeksleyip arama yapılabilmesini sağlayan, **Serverless (Sunucusuz)** ve tam otomatik bir arama motoru mimarisidir. Google altyapısına benzer "MapReduce" mantığını bulut üzerinde uygular.

## 💻 Kullanılan Teknolojiler
- **AWS S3:** Ham verileri, Map çıktılarını ve endeksi depolar. Frontend'i barındırır.
- **AWS Lambda:** Veri işleme (Mapper/Reducer) ve arama (Search) işlemlerini sunucusuz çalıştırır.
- **AWS API Gateway:** Kullanıcının arama isteklerini Search Lambda'sına iletir.
- **Python:** Veri çekme, metin işleme ve TF-IDF (MapReduce) algoritmaları için kullanılır.
- **HTML/CSS/JS:** Trabzonspor temalı, animasyonlu modern arayüz (SPA) için kullanılmıştır.

## ⚙️ MapReduce Mimarisi
- **Mapper:** S3'e yeni bir makale (`.json`) eklendiği an *otomatik* tetiklenir. Metni kelimelere böler, frekanslarını sayar ve sonucu `map-output/` klasörüne yazar. S3'e 500 dosya atarsanız, 500 Mapper eşzamanlı ve paralel çalışır.
- **Reducer:** Mapper'lar işini bitirdikten sonra tetiklenir. Tüm parçalanmış verileri toplar, TF-IDF skorlamasını hesaplar ve arama motorunun kullanacağı devasa `inverted_index.json` ana sözlüğünü oluşturur.

## 📂 Dosyalama
- `arama-motoru/scripts/`: `mapper.py`, `reducer.py`, `search.py` ve arayüz `index.html` dosyaları.
- `arama-motoru/data/`: Wikipedia'dan indirilen JSON makalelerinin yerel kopyası.
- `aws_setup.ps1`: Tüm AWS IAM, Lambda, S3 ve API Gateway altyapısını sıfırdan otomatik kurar.
- `fetch_fast.py` & `load_test.ps1`: Wikipedia'dan rastgele makale çekip AWS yük testi başlatır.

## 📊 Veri
Sistem, girdi olarak "title", "url" ve "text" içeren JSON formatlı makaleler kabul eder. Test aşamasında Wikipedia API'si üzerinden 500'den fazla makale çekilmiş ve tek seferde S3'e yüklenerek 8.000'den fazla benzersiz kelime endekslenmiştir.

## 🚀 Kullanım
1. `index.html` S3 üzerinde yayındadır. İlgili S3 statik websitesi URL'sine girilir.
2. Arama çubuğuna "tarih", "sanat", "futbol" gibi aranmak istenen kelime yazılır.
3. API üzerinden AWS Search Lambda'ya istek gider, önceden Reducer'ın hazırladığı endeks taranır ve en yüksek TF-IDF skoruna sahip sonuçlar arayüzde anında listelenir.
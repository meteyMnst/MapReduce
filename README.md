# Bordo Mavi Bulut Arama Motoru 🔴🔵

## 🎯 Proje Amacı
Bu proje, devasa boyutlardaki metin verilerini hızlı bir şekilde endeksleyip arama yapılabilmesini sağlayan, **Serverless (Sunucusuz)** ve tam otomatik bir arama motoru mimarisidir. Google altyapısına benzer "MapReduce" mantığını bulut üzerinde uygular.

## ☁️ AWS'nin Rolü ve Nerede Kullanıldığı
Tüm mimari **AWS (Amazon Web Services)** üzerinde %100 Serverless (sunucusuz) olarak çalışır. Hiçbir geleneksel sunucu kullanılmaz:
- **AWS S3:** Projenin kalbidir. Hem veritabanı (ham verileri ve endeks dosyalarını depolama) hem de Frontend (statik web sitesi arayüzünü barındırma) olarak kullanılır.
- **AWS Lambda:** Verileri aynı anda parçalamak (Mapper), hesaplayıp birleştirmek (Reducer) ve kullanıcının arama sorgularını anlık işlemek (Search) için sadece tetiklendikçe çalışır.
- **AWS API Gateway:** Kullanıcının arayüzden yaptığı aramaları güvenli bir şekilde Search Lambda'sına ileten köprüdür.

## 📊 Verinin Toplanması ve Depolanması
- **Veri Nasıl Toplandı?**: Sistemin verileri, `fetch_fast.py` Python betiği kullanılarak **Wikipedia API**'sinden canlı ve rastgele makaleler çekilerek toplanır. Çekilen her makalenin başlığı, URL'si ve içerik metni otomatik olarak alınır.
- **Veri Nasıl Depolanıyor?**: Toplanan devasa veriler önce parçalanarak tekil `.json` dosyalarına dönüştürülür. Daha sonra tamamı **AWS S3** bucket'ına yüklenir. S3'e düşen her ham dosya (raw-pages), MapReduce işleminden geçtikten sonra yine AWS S3 üzerinde ana endeks dosyası (inverted_index.json) olarak bulutta güvenle depolanır.

## ⚙️ MapReduce Mimarisi
- **Mapper:** S3'e yeni bir makale yüklendiği an *otomatik* tetiklenir. Metni kelimelere böler, frekanslarını sayar ve `map-output/` klasörüne yazar. S3'e 500 dosya atarsanız, 500 AWS Lambda fonksiyonu eşzamanlı çalışır.
- **Reducer:** Parçalanan verileri toplar, TF-IDF skorlamasını hesaplar ve arama motorunun kullanacağı devasa ana sözlüğü oluşturur.

## 📂 Dosyalama
- `arama-motoru/scripts/`: `mapper.py`, `reducer.py`, `search.py` ve Trabzonspor temalı `index.html` arayüz dosyası.
- `aws_setup.ps1`: Tüm AWS IAM, Lambda, S3 ve API altyapısını otomatik kuran powershell betiği.

## 🚀 Kullanım
1. `index.html` S3 üzerinde yayındadır. Arama sayfasına gidilir.
2. Aranmak istenen kelime yazılır.
3. API Gateway üzerinden AWS Lambda'ya istek gider, S3'teki endeks taranır ve en yüksek skora sahip sonuçlar anında listelenir.
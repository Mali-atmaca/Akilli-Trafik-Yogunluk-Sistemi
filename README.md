# Akıllı Trafik Yoğunluk Tahmin Modeli 🚦

Bu proje, geçmiş trafik verilerini kullanarak canlı veri akışları üzerinden anlık trafik yoğunluğu tahmini yapan uçtan uca (end-to-end) bir analitik sistemdir.

## 🚀 Proje Hakkında
Proje, büyük veri işleme araçları ve makine öğrenmesi tekniklerini bir araya getirerek şehir içi trafik optimizasyonuna çözüm sunmayı amaçlar. Veriler, performans odaklı **Parquet** formatında saklanmakta ve modelleme süreçleri bu yapı üzerinden yürütülmektedir.

## 🛠️ Kullanılan Teknolojiler
* [cite_start]**Dil:** Python 
* [cite_start]**Veri İşleme:** Pandas, NumPy 
* [cite_start]**Depolama:** Apache Parquet (Data Lake yapısı) 
* [cite_start]**Konteynerleştirme:** Docker & Docker Compose 
* [cite_start]**Web/Dashboard:** Flask/Dash (app.py ve templates üzerinden) 
* [cite_start]**Versiyon Kontrolü:** Git & GitHub 

## 📁 Proje Yapısı
* [cite_start]`data_lake/`: Verilerin saklandığı yapılandırılmış depolama alanı. 
* [cite_start]`models/`: Eğitilmiş makine öğrenmesi modelleri. 
* [cite_start]`templates/`: Dashboard arayüz dosyaları. 
* [cite_start]`Scripts/`: Veri işleme ve otomasyon betikleri. 
* [cite_start]`app.py`: Ana uygulama ve API giriş noktası. 
* [cite_start]`docker-compose.yml`: Projenin izole bir ortamda çalışmasını sağlayan yapılandırma. 

## 📦 Kurulum ve Çalıştırma
1. Projeyi klonlayın:
   ```bash
   git clone [https://github.com/Mali-atmaca/proje-adi.git](https://github.com/Mali-atmaca/proje-adi.git)
2.Docker ile tüm sistemi ayağa kaldırın:

Bash
docker-compose up
Veri Seti Notu
Proje boyutunu optimize etmek amacıyla ham veri seti bu depoda paylaşılmamıştır. Test verilerine erişmek veya kendi verinizi entegre etmek için Scripts/ klasöründeki yönergeleri izleyebilirsiniz.

📄 Lisans
Bu proje MIT Lisansı ile korunmaktadır. Detaylar için LICENSE dosyasına bakabilirsiniz. 


**Neden Bu README?** klasör yapında gördüğüm `docker-compose.yml`, `data_lake` ve `templates` klasörleri senin sadece kod yazmadığını, aynı zamanda sistemi paketleyebildiğini ve görselleştirebildiğini gösteriyor. Bu README, bu yetkinliklerini mülakatçılara "bağıran" profesyonel bir vitrindir.

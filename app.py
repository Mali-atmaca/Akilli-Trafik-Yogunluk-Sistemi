from flask import Flask, render_template, jsonify
import redis
import json

app = Flask(__name__)

# Redis Bağlantısı: Spark'ın saniyede bir güncellediği veriyi buradan okuyacağız.
# decode_responses=True önemli, aksi halde veri byte formatında (b'...') gelir.
try:
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    r.ping() # Redis açık mı diye kontrol et
    print("✅ Web Sunucusu Redis'e başarıyla bağlandı.")
except Exception as e:
    print(f"❌ Redis Bağlantı Hatası: Lütfen Redis sunucusunun çalıştığından emin olun. Hata: {e}")

@app.route('/')
def index():
    # templates klasörü içindeki index.html dosyasını tarayıcıya gönderir
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    try:
        # Spark'ın Redis'e "guncel_trafik" adıyla kaydettiği son JSON verisini çek
        data_str = r.get("guncel_trafik")
        if data_str:
            data = json.loads(data_str)
            return jsonify(data)
        else:
            return jsonify({"error": "Veri Bekleniyor..."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🌐 Web Dashboard Başlatılıyor...")
    print("👉 Tarayıcınızda şu adrese gidin: http://127.0.0.1:5000")
    # debug=False yapıyoruz çünkü üretim ortamı simülasyonundayız.
    app.run(host='0.0.0.0', port=5000, debug=False)
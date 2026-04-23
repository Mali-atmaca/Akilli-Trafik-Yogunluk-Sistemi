import os
import pandas as pd
import xgboost as xgb

print("🟢 Akıllı Trafik Canlı Tahmin Sistemi Başlatılıyor...")

# 1. Eğittiğimiz Beyni (Modeli) Bul ve Yükle
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, '..', 'models', 'traffic_model_v2.json')

if not os.path.exists(model_path):
    print("❌ HATA: Model dosyası bulunamadı! Önce eğitimi tamamlamalısın.")
    exit()

# XGBoost modelini yüklüyoruz
model = xgb.XGBRegressor()
model.load_model(model_path)
print("🧠 Yapay Zeka Beyni Yüklendi! Tahmine Hazır.\n")

# 2. Canlı Veri Simülasyonu (Sanki sensörlerden anlık veri geliyormuş gibi)
# Senaryo: SegmentID'si 150 olan yolda, Çarşamba günü (2), Saat 17:00 (İş çıkışı), anlık 850 araç var.
canli_veri = pd.DataFrame({
    'SegmentID': [150], 
    'HH': [17],          # Saat (0-23 arası)
    'DayOfWeek': [2],    # Gün (0:Pzt, 1:Sal, 2:Çar, 3:Per, 4:Cum, 5:Cts, 6:Paz)
    'Vol': [850]         # Şu anki araç sayısı
})

print(f"📡 SENSÖR VERİSİ GELDİ:")
print(f"📍 Yol ID: {canli_veri['SegmentID'][0]} | 🕒 Saat: {canli_veri['HH'][0]}:00 | 🚗 Mevcut Araç: {canli_veri['Vol'][0]}")

# 3. Geleceği Tahmin Et
gelecek_tahmin = model.predict(canli_veri)
beklenen_arac = int(gelecek_tahmin[0])

print("-" * 50)
print(f"🔮 YAPAY ZEKA TAHMİNİ:")
print(f"⏭️ 1 Saat Sonra Beklenen Araç Sayısı: {beklenen_arac}")

# Basit bir Akıllı Şehir Karar Mekanizması
if beklenen_arac > canli_veri['Vol'][0] + 50:
    print("🚨 UYARI: Trafik artacak! Yeşil ışık süreleri uzatılıyor...")
elif beklenen_arac < canli_veri['Vol'][0] - 50:
    print("✅ BİLGİ: Trafik rahatlayacak. Standart ışık döngüsüne geçiliyor.")
else:
    print("➖ BİLGİ: Trafik stabil kalacak.")
print("-" * 50)
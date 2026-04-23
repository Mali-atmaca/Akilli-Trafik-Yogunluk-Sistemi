from kafka import KafkaProducer
import json
import time
import random
import datetime

print("🟢 Profesyonel Kafka Producer Başlatılıyor...")

try:
    producer = KafkaProducer(
        bootstrap_servers=['127.0.0.1:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception as e:
    print(f"❌ Kafka'ya bağlanılamadı: {e}")
    exit()

topic_name = "nyc_traffic_live"
ornek_yollar = [116, 150, 202, 310, 455, 890]

# ⚡ DÜZELTME 4: Geçmiş Veri (State) Tutma Mekanizması
prev_values = {}

try:
    while True:
        segment = random.choice(ornek_yollar)
        
        # Gerçekçi zaman serisi davranışı
        if segment in prev_values:
            prev = prev_values[segment]
        else:
            prev = random.randint(200, 800)
            
        current = int(prev * random.uniform(0.8, 1.2)) # ±%20 değişim
        prev_values[segment] = current
        
        # ⚡ DÜZELTME 3: Gerçek Zamanlı Saat Kullanımı
        now = datetime.datetime.now()
        
        data = {
            "SegmentID": segment,
            "HH": now.hour,
            "DayOfWeek": now.weekday(),
            "Vol": current,
            "PrevVol": prev
        }
        
        producer.send(topic_name, value=data)
        print(f"📤 Giden Veri: {data}")
        
        time.sleep(2) 

except KeyboardInterrupt:
    print("\n🛑 Veri akışı durduruldu.")
    producer.close()
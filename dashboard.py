import streamlit as st
import redis
import json
import time

st.set_page_config(page_title="NYC Akıllı Trafik Lambda Yönetimi", page_icon="🚦", layout="wide")

# CSS ile biraz estetik katalım
st.markdown("""
    <style>
    .big-font {font-size:20px !important; font-weight: bold;}
    .anomaly-box {background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;}
    .normal-box {background-color: #00cc96; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("🚦 Lambda Architecture: Real-Time Traffic Management")
st.markdown("Apache Kafka **Streaming** & MongoDB **Batch Layer** Fusion via XGBoost")
st.markdown("---")

@st.cache_resource
def get_redis_connection():
    try:
        return redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    except:
        return None

r = get_redis_connection()

if not r:
    st.error("❌ Redis'e bağlanılamadı! Lütfen Redis'i başlatın.")
    st.stop()

yollar = [116, 150, 202, 310, 455, 890]
placeholder = st.empty()

while True:
    with placeholder.container():
        cols = st.columns(3) # Yolları 3 sütun halinde dizelim (2 satır olur)
        
        for idx, yol_id in enumerate(yollar):
            raw_data = r.get(f"yol_{yol_id}_durum")
            
            # Sütun hesaplama (3 sütunlu grid)
            col = cols[idx % 3]
            
            with col:
                st.markdown(f"### 📍 Yol Segmenti: {yol_id}")
                
                if raw_data:
                    data = json.loads(raw_data)
                    canli = int(data.get('Vol', 0))
                    gecmis = int(data.get('PrevVol', 0))
                    tarihi_ort = int(data.get('Tarihi_Ortalama', 0))
                    ml_tahmin = int(data.get('gelecek_tahmin', 0))
                    fusion_skor = int(data.get('Lambda_Final_Score', 0))
                    anomali = data.get('Is_Anomaly', False)
                    saat = data.get('HH', 0)
                    
                    st.caption(f"🕒 Saat: {saat}:00 | Geçmiş Saat Hacmi: {gecmis}")
                    
                    if anomali:
                        st.markdown('<div class="anomaly-box">🚨 ANOMALİ DETECTED (Tarihi Ortalamanın Çok Üzerinde!)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="normal-box">✅ AKIŞ NORMAL</div>', unsafe_allow_html=True)
                        
                    st.write("") # Boşluk
                    
                    # Metrikler
                    sub_cols = st.columns(2)
                    with sub_cols[0]:
                        st.metric(label="Canlı Sensör (Vol)", value=canli, delta=canli-gecmis, delta_color="inverse")
                    with sub_cols[1]:
                        st.metric(label="Tarihi Ortalama (Batch)", value=tarihi_ort)
                        
                    st.metric(label="🔮 AI FUSION TAHMİNİ (1 Saat Sonra)", value=fusion_skor, delta=fusion_skor-canli, delta_color="inverse")
                    st.markdown("---")
                else:
                    st.info("Sinyal Bekleniyor...")
                    st.markdown("---")
                    
    time.sleep(1.5) # Dashboard'u 1.5 saniyede bir yenile
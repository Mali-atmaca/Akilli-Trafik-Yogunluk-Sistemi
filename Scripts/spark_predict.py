from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, IntegerType
import os
import pandas as pd
import xgboost as xgb
from pymongo import MongoClient
import redis
import json

# --- SPARK AYARLARI ---
os.environ['TEMP'] = 'C:\\spark_temp'
os.environ['TMP'] = 'C:\\spark_temp'
os.makedirs('C:\\spark_temp', exist_ok=True)
os.environ['HADOOP_HOME'] = 'C:\\hadoop'
os.environ['PATH'] = os.environ.get('PATH', '') + ';C:\\hadoop\\bin'
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 pyspark-shell'

spark = SparkSession.builder.appName("Zirhli_Trafik_Lambda_Architecture").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

print("🧠 Model ve Veritabanları Yükleniyor...")
model = xgb.XGBRegressor()
# ⚡ DÜZELTME 5: Model Versiyonlama (İsimlendirme prod standardı)
model.load_model(os.path.join(os.path.dirname(__file__), '..', 'models', 'traffic_model_v2.json'))

# Veritabanı Bağlantıları
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
mongo_client = MongoClient("mongodb://127.0.0.1:27017/")
db = mongo_client["AkilliTrafikDB"]

# ⚡ DÜZELTME 2: MongoDB Query Performansı için Indexleme (Çok Kritik!)
db.historical_stats.create_index([("SegmentID", 1), ("HH", 1)])

data_lake_path = os.path.join(os.path.dirname(__file__), '..', 'data_lake', 'traffic_parquet')

schema = StructType([
    StructField("SegmentID", IntegerType(), True),
    StructField("HH", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True),
    StructField("Vol", IntegerType(), True),
    StructField("PrevVol", IntegerType(), True)
])

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "127.0.0.1:9092") \
    .option("subscribe", "nyc_traffic_live") \
    .option("startingOffsets", "latest") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), schema).alias("data")).select("data.*")

def process_live_data(batch_df, batch_id):
    # ⚡ DÜZELTME 7: isEmpty() yerine güvenli count() kontrolü
    if batch_df.count() == 0: 
        return
    
    # ⚡ DÜZELTME 3: Schema Evolution (mergeSchema eklendi)
    try:
        batch_df.write.mode("append") \
            .option("mergeSchema", "true") \
            .partitionBy("SegmentID", "DayOfWeek") \
            .parquet(data_lake_path)
    except Exception as e:
        print(f"Data Lake Yazma Hatası: {e}")
    
    raw_pdf = batch_df.toPandas()
    db_records = []
    
    for index, row in raw_pdf.iterrows():
        latest = row.to_dict()
        vol = int(latest['Vol'])
        segment = int(latest['SegmentID'])
        
        # ⚡ DÜZELTME 1: PrevVol (Geçmiş Hacim) artık REDIS üzerinden (Distributed State) yönetiliyor
        prev_key = f"yol_{segment}_prev"
        try:
            prev_from_redis = r.get(prev_key)
            if prev_from_redis:
                latest['PrevVol'] = int(prev_from_redis)
            else:
                latest['PrevVol'] = vol # İlk çalışma için fallback
                
            r.set(prev_key, vol) # Bir sonraki batch için şu anki veriyi Redis'e kaydet
        except Exception as e:
            print(f"Redis State Hatası: {e}")

        # Batch Layer'dan Ortalama Çekme
        try:
            historical = db["historical_stats"].find_one({"SegmentID": segment, "HH": latest['HH']})
            tarihi_ortalama = int(historical['Ortalama_Arac']) if historical else 500
        except:
            tarihi_ortalama = 500
            
        latest['Tarihi_Ortalama'] = tarihi_ortalama
        
        # XGBoost Tahmini
        features = ['SegmentID', 'HH', 'DayOfWeek', 'Vol', 'PrevVol']
        X_canli = pd.DataFrame([latest])[features]
        latest['gelecek_tahmin'] = int(model.predict(X_canli)[0])
        
        # ⚡ DÜZELTME 6: LAMBDA FUSION (Serving Layer Combine Logic)
        # Gerçek Lambda Mimarisi: Canlı ML tahmini ile Batch geçmiş ortalamasını birleştir (Ensemble)
        latest['Lambda_Final_Score'] = int((latest['gelecek_tahmin'] + tarihi_ortalama) / 2)
        
        # Anomali Tespiti (Fusion Skoru üzerinden)
        is_anomaly = True if vol > (tarihi_ortalama * 2) else False
        latest['Is_Anomaly'] = is_anomaly
        
        # ⚡ DÜZELTME 4: Veritabanı Error Handling (Prod-Level)
        try:
            r.set(f"yol_{segment}_durum", json.dumps(latest))
            db_records.append(latest)
        except Exception as e:
            print(f"Redis Yazma Hatası: {e}")
        
        uyari = "🚨 ANOMALİ!" if is_anomaly else "✅ Normal"
        print(f"Yol: {segment} | Canlı: {vol} (Tarihi Ort: {tarihi_ortalama}) -> ML Tahmin: {latest['gelecek_tahmin']} -> 🧠 FUSION SKOR: {latest['Lambda_Final_Score']} [{uyari}]")

    try:
        if db_records:
            db["nyc_canli_veri"].insert_many(db_records)
    except Exception as e:
        print(f"MongoDB Insert Hatası: {e}")

query = json_df.writeStream.foreachBatch(process_live_data).option("checkpointLocation", "C:\\spark_checkpoints\\nyc_traffic_v6").start()
query.awaitTermination()
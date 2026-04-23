from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, round
import os

# --- SPARK AYARLARI ---
os.environ['HADOOP_HOME'] = 'C:\\hadoop'
os.environ['PATH'] = os.environ.get('PATH', '') + ';C:\\hadoop\\bin'

print("🏗️ Spark Batch Processing (Geçmiş Veri Analizi) Başlatılıyor...")

# 1. Spark Session Başlat
spark = SparkSession.builder \
    .appName("NYC_Traffic_Batch_Layer") \
    .master("local[*]") \
    .config("spark.mongodb.write.connection.uri", "mongodb://127.0.0.1:27017/AkilliTrafikDB.historical_stats") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Geçmiş Veriyi (CSV) Oku
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'DOT_Traffic_Speeds_24_Hours.csv')

print(f"📂 Veri okunuyor: {data_path}")
df = spark.read.csv(data_path, header=True, inferSchema=True)

# 3. VERİ ANALİZİ (Aggregation)
# Yolların günlere ve saatlere göre ORTALAMA ve MAKSİMUM araç yoğunluğunu hesaplıyoruz
print("⚙️ Devasa veri seti üzerinde istatistikler hesaplanıyor...")

agg_df = df.groupBy("SegmentID", "DayOfWeek", "HH") \
    .agg(
        round(avg("Vol"), 0).alias("Ortalama_Arac"),
        max("Vol").alias("Maksimum_Arac")
    ) \
    .orderBy("SegmentID", "DayOfWeek", "HH")

# Sadece örnek olması için ekranda ilk 10 satırı göster
agg_df.show(10)

# 4. Veritabanına Yaz (MongoDB - Historical Data)
# Hocaya "İşte Data Warehouse / Batch Layer'ımız" diyeceğin kısım
try:
    print("🗄️ Sonuçlar MongoDB 'historical_stats' koleksiyonuna yazılıyor...")
    agg_df.write.format("mongo").mode("overwrite").save()
    print("✅ BATCH İŞLEMİ BAŞARIYLA TAMAMLANDI!")
except Exception as e:
    print(f"⚠️ MongoDB kapalı olabilir (İşlem ekranda gösterildi): {e}")

spark.stop()
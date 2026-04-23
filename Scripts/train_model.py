import os
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'DOT_Traffic_Speeds_24_Hours.csv')

print("✅ Veri Okunuyor...")
df = pd.read_csv(data_path, nrows=1000000)

time_cols = df[['Yr', 'M', 'D', 'HH', 'MM']].rename(columns={'Yr': 'year', 'M': 'month', 'D': 'day', 'HH': 'hour', 'MM': 'minute'})
df['DATE_TIME'] = pd.to_datetime(time_cols)
df['DayOfWeek'] = df['DATE_TIME'].dt.dayofweek

# ⚡ DÜZELTME 1: Zaman Sıralaması artık tamamen DATE_TIME üzerinden yapılıyor
df = df.sort_values(by=['SegmentID', 'DATE_TIME'])

# Özellik Mühendisliği (Feature Engineering)
df['PrevVol'] = df.groupby('SegmentID')['Vol'].shift(1)
df['FutureVol'] = df.groupby('SegmentID')['Vol'].shift(-1)
df = df.dropna()

print("🚀 XGBoost Modeli Zaman Serisi Mantığıyla Eğitiliyor...")
X = df[['SegmentID', 'HH', 'DayOfWeek', 'Vol', 'PrevVol']]
y = df['FutureVol']

# ⚡ DÜZELTME 2: Time-Aware Split (Rastgele bölme kaldırıldı)
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1)
model.fit(X_train, y_train)

error = mean_absolute_error(y_test, model.predict(X_test))
print(f"📈 YENİ Ortalama Hata: {error:.2f} Araç")

model_dir = os.path.join(script_dir, '..', 'models')
os.makedirs(model_dir, exist_ok=True)
model.save_model(os.path.join(model_dir, 'traffic_model_v2.json'))
print("📁 Model Başarıyla Kaydedildi.")
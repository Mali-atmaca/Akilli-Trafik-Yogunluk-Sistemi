import pandas as pd
import os

# 1. Dev dosyanın adını buraya tam yaz (Senin indirdiğin dosyanın adını kontrol et!)
input_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'US_Accidents_March23.csv') 
output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'accidents_subset.csv')

print("Dev kaza veri seti taranıyor... Bu biraz sürebilir.")

use_cols = ['Severity', 'Start_Time', 'State', 'Description', 'Visibility(mi)']

try:
    chunk_list = []
    for chunk in pd.read_csv(input_path, usecols=use_cols, chunksize=50000):
        # Sadece Minnesota (MN) eyaletini ve boş olmayanları alıyoruz
        filtered_chunk = chunk[chunk['State'] == 'MN'].dropna()
        chunk_list.append(filtered_chunk)
    
    df_subset = pd.concat(chunk_list)
    
    # DÜZELTİLEN KISIM BURASI: format='mixed' parametresi eklendi
    df_subset['Start_Time'] = pd.to_datetime(df_subset['Start_Time'], format='mixed').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df_subset.to_csv(output_path, index=False)
    print(f"Başarılı! 10 GB'lık devden {len(df_subset)} satırlık tertemiz bir veri çıkardık.")
    print(f"Yeni dosyan: {output_path}")

except Exception as e:
    print(f"Hata oluştu: {e}")
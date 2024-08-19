import pandas as pd

# CSV 파일 로드
file_path = 'data/output_with_area4.csv'  # 기존 파일 경로
data = pd.read_csv(file_path)

# LON과 LAT 값이 있는 행만 필터링
filtered_data = data[(data['LON'].notna()) & (data['LAT'].notna()) & (data['LON'] != '') & (data['LAT'] != '')]

# 결과를 새로운 CSV 파일로 저장
output_file = 'data/output_with_area5.csv'
filtered_data.to_csv(output_file, index=False, encoding='utf-8')

print(f"LON, LAT 값이 있는 행들이 {output_file}에 저장되었습니다.")

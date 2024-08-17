import pandas as pd

# 한라산의 경위도
hallasan_lon = 126.52917
hallasan_lat = 33.36167

# CSV 파일 로드
df = pd.read_csv('data/output.csv')

# 경위도를 기준으로 지역 분류 함수
def determine_area(row):
    if row['LAT'] > hallasan_lat and row['LON'] > hallasan_lon:
        return '북동'
    elif row['LAT'] > hallasan_lat and row['LON'] < hallasan_lon:
        return '북서'
    elif row['LAT'] < hallasan_lat and row['LON'] > hallasan_lon:
        return '남동'
    elif row['LAT'] < hallasan_lat and row['LON'] < hallasan_lon:
        return '남서'
    return 'Unknown'  # 예외 처리

# 새로운 'AREA' 컬럼 추가
df['AREA'] = df.apply(determine_area, axis=1)

# 결과를 확인하거나 저장
df.to_csv('data/output_with_area.csv', index=False)

print(df.head())

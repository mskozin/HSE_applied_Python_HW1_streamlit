import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import time

def analyze_city(city_data):
    """Анализ данных для одного города"""
    df = city_data.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Скользящее среднее (30 дней) и отклонение
    df['rolling_mean'] = df['temperature'].rolling(window=30, center=True).mean()
    df['rolling_std'] = df['temperature'].rolling(window=30, center=True).std()
    
    # Определение аномалий: за пределы ±2σ
    df['anomaly'] = np.abs(df['temperature'] - df['rolling_mean']) > (2 * df['rolling_std'])
    
    # Метрики (срденее и стандартное отклонение) по сезонам
    seasonal_stats = df.groupby('season').agg(
        avg_temp=('temperature', 'mean'),
        std_temp=('temperature', 'std')
    ).round(2)
    
    # Долгосрочный тренд (линейная регрессия)
    df['day_num'] = (df['timestamp'] - df['timestamp'].min()).dt.days
    trend_coeff = np.polyfit(df['day_num'], df['temperature'], 1)[0]
    
    return {
        'city': df['city'].iloc[0],
        'data': df,
        'seasonal_stats': seasonal_stats,
        'trend_per_year': trend_coeff * 365.25  # Переводим в градусы/год
    }

def parallel_analysis(df):
    """Распараллеленный анализ по городам"""
    start_time = time.time()
    
    # Разделяем данные по городам
    city_groups = [group for _, group in df.groupby('city')]
    
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(analyze_city, city_groups))
    
    print(f"Параллельный анализ: {time.time() - start_time:.2f} секунд")
    return {r['city']: r for r in results}

def sequential_analysis(df):
    """Последовательный анализ для сравнения"""
    start_time = time.time()
    results = {}
    
    for city, group in df.groupby('city'):
        results[city] = analyze_city(group)
    
    print(f"Последовательный анализ: {time.time() - start_time:.2f} секунд")
    return results


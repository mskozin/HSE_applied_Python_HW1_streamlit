import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from weather_api import WeatherAPI, check_anomaly
# from analysis import parallel_analysis
from analysis import sequential_analysis


st.set_page_config(page_title="Анализ температур", layout="wide")

# Заголовок
st.title("🌡 Анализ температурных данных и мониторинг")
st.markdown("---")

# Загрузка файла
uploaded_file = st.file_uploader("Загрузите файл temperature_data.csv", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    # Используем демо-данные
    # import sys
    # sys.path.append('.')
    df = pd.read_csv('temperature_data.csv')

# Боковая панель
st.sidebar.header("Настройки")

# Выбор города
cities = df['city'].unique() if 'city' in df.columns else []
selected_city = st.sidebar.selectbox("Выберите город:", cities)

# Ввод API ключа
api_key = st.sidebar.text_input("Введите OpenWeatherMap API ключ:", type="password")
if api_key:
    st.sidebar.info("Ключ введен")
else:
    st.sidebar.warning("Введите API ключ для получения текущей погоды")

# Кнопка для анализа
if st.sidebar.button("Запустить анализ", type="primary"):
    if selected_city:
        with st.spinner("Анализируем данные..."):
            # Анализ исторических данных
            # results = parallel_analysis(df) (# не использую, потому что эксперименты показали, что множество процессов для такого размера датасета работают медленее)
            results = sequential_analysis(df)
            city_data = results[selected_city]
            
            # Создаем вкладки
            tab1, tab2, tab3, tab4 = st.tabs(["Исторические данные", "Аномалии", "Сезонные профили", "Текущая погода"])
            
            with tab1:
                # Описательная статистика
                st.subheader(f"📊 Описательная статистика для {selected_city}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Средняя температура", f"{city_data['data']['temperature'].mean():.1f}°C")
                with col2:
                    st.metric("Максимальная", f"{city_data['data']['temperature'].max():.1f}°C")
                with col3:
                    st.metric("Минимальная", f"{city_data['data']['temperature'].min():.1f}°C")
                with col4:
                    trend = city_data['trend_per_year']
                    st.metric("Тренд", f"{trend:+.2f}°C/год", 
                             delta="Рост" if trend > 0 else "Спад")
                
                # Временной ряд
                st.subheader("📈 Временной ряд температур")
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(
                    x=city_data['data']['timestamp'], 
                    y=city_data['data']['temperature'],
                    mode='lines',
                    name='Температура',
                    line=dict(color='blue', width=1)
                ))
                fig1.add_trace(go.Scatter(
                    x=city_data['data']['timestamp'],
                    y=city_data['data']['rolling_mean'],
                    mode='lines',
                    name='Скользящее среднее (30 дней)',
                    line=dict(color='red', width=2)
                ))
                fig1.update_layout(
                    title=f"Температура в {selected_city}",
                    xaxis_title="Дата",
                    yaxis_title="Температура (°C)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with tab2:
                # Аномалии
                st.subheader("⚠️ Обнаруженные аномалии")
                anomalies = city_data['data'][city_data['data']['anomaly']]
                
                if not anomalies.empty:
                    st.subheader("Аномальные значения на графике температур")
                    fig2 = go.Figure()
                    
                    # Нормальные точки
                    normal_data = city_data['data'][~city_data['data']['anomaly']]
                    fig2.add_trace(go.Scatter(
                        x=normal_data['timestamp'], 
                        y=normal_data['temperature'],
                        mode='markers',
                        name='Норма',
                        marker=dict(color='blue', size=4)
                    ))
                    
                    # Аномалии
                    fig2.add_trace(go.Scatter(
                        x=anomalies['timestamp'], 
                        y=anomalies['temperature'],
                        mode='markers',
                        name='Аномалии',
                        marker=dict(color='red', size=8, symbol='x')
                    ))
                    
                    fig2.update_layout(
                        title=f"Аномалии температуры в {selected_city}",
                        xaxis_title="Дата",
                        yaxis_title="Температура (°C)",
                        showlegend=True
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                    st.subheader("Аномальные значения в виде таблицы")                    
                    st.dataframe(anomalies[['timestamp', 'temperature']].sort_values('timestamp', ascending=False))
                else:
                    st.success("Аномалий не обнаружено")
            
            with tab3:
                # Сезонные профили
                st.subheader("🍂 Сезонные профили")
                
                fig3 = make_subplots(rows=1, cols=2, 
                                    subplot_titles=("Средняя температура по сезонам", 
                                                   "Стандартное отклонение по сезонам"))
                
                # Средние температуры
                fig3.add_trace(
                    go.Bar(x=city_data['seasonal_stats'].index,
                          y=city_data['seasonal_stats']['avg_temp'],
                          name='Средняя темп.',
                          marker_color='coral'),
                    row=1, col=1
                )
                
                # Стандартное отклонение
                fig3.add_trace(
                    go.Bar(x=city_data['seasonal_stats'].index,
                          y=city_data['seasonal_stats']['std_temp'],
                          name='Станд. отклонение по сезонам',
                          marker_color='lightblue'),
                    row=1, col=2
                )
                
                fig3.update_layout(height=400, showlegend=False)
                fig3.update_yaxes(title_text="Температура (°C)", row=1, col=1)
                fig3.update_yaxes(title_text="Температура (°C)", row=1, col=2)
                
                st.plotly_chart(fig3, use_container_width=True)
                
                # Таблица с сезонной статистикой
                st.subheader("Среднее значение и стандартное отклонение в виде таблицы")
                st.dataframe(city_data['seasonal_stats'])
            
            with tab4:
                # Текущая погода через API
                st.subheader("🌤 Текущая погода")
                
                if api_key:                    
                    # Асинхронный запрос (не использую, потому что делаем только 1 запрос)
                    # async def get_weather():
                    #     async with aiohttp.ClientSession() as session:
                    #         api = WeatherAPI(api_key)
                    #         return await api.get_current_weather_async(selected_city)
                    
                    # try:
                    #     # Запускаем асинхронный запрос
                    #     import asyncio
                    #     weather = asyncio.run(get_weather())
                    try:
                        # синхронный запрос
                        api = WeatherAPI(api_key)
                        weather = api.get_current_weather_sync(selected_city)

                        if 'error' in weather:
                            if weather.get('cod') == 401:
                                st.error("❌ Неверный API ключ. Проверьте ключ или зарегистрируйтесь на openweathermap.org")
                            else:
                                st.error(f"Ошибка: {weather['error']}")
                        else:
                            # Определяем текущий сезон
                            from datetime import datetime
                            month = datetime.now().month
                            season = "winter" if month in [12,1,2] else "spring" if month in [3,4,5] else "summer" if month in [6,7,8] else "autumn"
                            
                            # Проверяем на аномалию
                            anomaly_status = check_anomaly(
                                weather['temperature'],
                                city_data['seasonal_stats'],
                                season
                            )
                            
                            # Отображаем информацию
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Текущая температура** {weather['temperature']:.1f}°C")
                                st.write(f"**Ощущается как** {weather['feels_like']:.1f}°C")
                                
                                st.write(f"**Статус:** {anomaly_status} температура")
                            
                            with col2:
                                st.write(f"**Влажность:** {weather['humidity']}%")
                                st.write(f"**Описание:** {weather['description']}")
                                st.write(f"**Время обновления:** {weather['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                                st.write(f"**Сезон для сравнения:** {season}")
                            
                            # Сравнение с историческими данными
                            st.subheader("📊 Сравнение с историческими данными")
                            
                            hist_avg = city_data['seasonal_stats'].loc[season, 'avg_temp']
                            hist_std = city_data['seasonal_stats'].loc[season, 'std_temp']
                            
                            fig4 = go.Figure()
                            
                            # Исторический диапазон
                            fig4.add_trace(go.Bar(
                                x=[season],
                                y=[4 * hist_std],
                                base=hist_avg - 2*hist_std,
                                name='Нормальный диапазон: среднее значение ±2σ для сезона',
                                marker_color='lightgreen',
                                width=0.5
                            ))

                            # Линия среднего значения
                            fig4.add_hline(
                            y=hist_avg,
                            line_dash="dash",
                            line_color="blue",
                            line_width=2,
                            annotation_text=f"Среднее значение для сезона: {hist_avg:.2f}°C",
                            annotation_position="top right",
                            name=f'Среднее значение для сезона: {hist_avg:.2f}°C'
                            )
                            
                            # Текущая температура
                            fig4.add_trace(go.Scatter(
                                x=[season],
                                y=[weather['temperature']],
                                mode='markers',
                                name='Текущая температура',
                                marker=dict(color='red', size=20, symbol='star')
                            ))
                            
                            fig4.update_layout(
                                title=f"Сравнение с сезонными нормами ({season})",
                                yaxis_title="Температура (°C)",
                                showlegend=True
                            )
                            
                            st.plotly_chart(fig4, use_container_width=True)
                            
                            # Комментарий
                            diff = weather['temperature'] - hist_avg
                            if anomaly_status == "АНОМАЛЬНАЯ":
                                st.warning(f"⚠️ Температура отличается от среднего значения для сезона на {diff:.1f}°C")
                            else:
                                st.success(f"✅ Температура в пределах сезонной нормы (отклонение от среднего значения {diff:+.1f}°C)")
                    
                    except Exception as e:
                        st.error(f"Ошибка при запросе к API: {str(e)}")
                
                else:
                    st.info("Для работы это вкладки необходимо ввесте API ключ в боковой панели и выбрать город в выпадающем списке для получения текущей погоды")
    
    else:
        st.error("Пожалуйста, выберите город")

# Информация о данных
st.sidebar.markdown("---")
st.sidebar.info("""
**Примечание:**
- Если не предоставлен файл с историческими данными, будет использован сгенерированный пример
- запустить анализ можно без API ключа, однако вкладка "Текущая погода" будет нефункциональна
""")
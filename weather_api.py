import requests
import aiohttp
from datetime import datetime

class WeatherAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def get_current_weather_sync(self, city):
        """Синхронный запрос текущей погоды"""
        if not self.api_key:
            return {"error": "API key not provided"}
        
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'timestamp': datetime.fromtimestamp(data['dt'])
                }
            else:
                return {"error": data.get('message', 'Unknown error'), "cod": data.get('cod')}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def get_current_weather_async(self, city):
        """Асинхронный запрос текущей погоды"""
        if not self.api_key:
            return {"error": "API key not provided"}
        
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        return {
                            'temperature': data['main']['temp'],
                            'feels_like': data['main']['feels_like'],
                            'humidity': data['main']['humidity'],
                            'description': data['weather'][0]['description'],
                            'timestamp': datetime.fromtimestamp(data['dt'])
                        }
                    else:
                        return {"error": data.get('message', 'Unknown error'), "cod": data.get('cod')}
                        
        except Exception as e:
            return {"error": str(e)}


# Здесь у меня возник вопрос. 
# При расчете аномалий в исторических данных мы использовали скользящее среднее и отклонения по скользящему значению для 30 дней. 
# Но в формулировке задания для текуще погоды указано так: " является ли текущая температура нормальной, исходя из исторических данных для текущего сезона."
# В этой функции я следовал букве задания и для текущей погоды считал аномальным выход за 2 сигма по сезону, а не по скользящему за 30 дней.
def check_anomaly(current_temp, historical_stats, season):
    """Проверка на аномальность текущей температуры"""
    if season not in historical_stats.index:
        return "Недостаточно данных"
    
    avg = historical_stats.loc[season, 'avg_temp']
    std = historical_stats.loc[season, 'std_temp']
    
    if abs(current_temp - avg) > 2 * std:
        return "АНОМАЛЬНАЯ"
    else:
        return "Нормальная"



# файл для экспериментов по сравнению синхронного и асинхронного подхода к http запросам в сервис OpenWeatherMap API  

from weather_api import WeatherAPI
import time
import asyncio

# место для вашего ключа
api_key = "выразительная заглушка"

# Синхронный
def multiple_requests_sync(cities):
    """синхронная функция для запроса погода для списка городов"""
    sync_start = time.time()
    sync_results = []
    for city in cities:
        sync_results.append(api.get_current_weather_sync(city))
    sync_time = time.time() - sync_start
    return(sync_time, sync_results)


# Асинхронный
async def multiple_requests_async(cities):
        """асинхронная функция для запроса погоды для списка городов"""
        async_start = time.time()
        tasks = [api.get_current_weather_async(city) for city in cities]
        async_results = await asyncio.gather(*tasks)
        async_time = time.time() - async_start
        return(async_time, async_results)


api = WeatherAPI(api_key) 
weather = api.get_current_weather_sync("Berlin")

cities = ["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"]
# cities = ["Berlin", "Cairo", "Dubai"]
# cities = ["Berlin"]

sync_time, sync_results = multiple_requests_sync(cities)
async_time, async_results = asyncio.run(multiple_requests_async(cities))


print(f"\n=== Сравнение методов ===")
print(f"Синхронный: {len(cities)} городов за {sync_time:.2f} секунд")
print(f"Асинхронный: {len(cities)} городов за {async_time:.2f} секунд")
print(f"Выигрыш: {sync_time/async_time:.1f}x")
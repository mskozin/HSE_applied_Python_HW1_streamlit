# Эксперимент с временем работы при распаралеливании работы
# Обе функции разбивают датасет по городам. (Не знаю, можно ли это назвать чанком) и проводит аналяз температур для отдельного города.
# либо последовательно, либо с использованием независимых процессов при помощи ProcessPoolExecutor из concurrent.futures

import pandas as pd
from analysis import sequential_analysis, parallel_analysis

df = pd.read_csv("temperature_data.csv")

if __name__ == '__main__':
    for i in range(10): #10 повторов эксперимента
        print("="*15)
        seq_results = sequential_analysis(df)
        par_results = parallel_analysis(df)
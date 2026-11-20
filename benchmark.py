import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def analyze_heavy_data(n: int) -> int:
    """
    Symulacja zadania mocno obciążającego procesor (CPU-bound).
    Wyobraź sobie, że to np. analiza statystyczna milionów logów albo kompresja plików.
    """
    s = 0
    for i in range(n):
        s += i * i
    return s

def run_benchmark(name: str, executor_class, tasks: list):
    """Uruchamia zadania we wskazanej puli (wątków lub procesów) i mierzy czas."""
    start_time = time.perf_counter()
    
    with executor_class(max_workers=4) as executor:
        list(executor.map(analyze_heavy_data, tasks))
        
    elapsed = time.perf_counter() - start_time
    print(f"{name:<25} | Czas wykonania: {elapsed:.4f} s")

if __name__ == "__main__":
    print("--- Test wpływu GIL na obliczenia (CPU-bound) ---")
    
    tasks_to_run = [5_000_000, 5_000_000, 5_000_000, 5_000_000]
    
    start_seq = time.perf_counter()
    for task in tasks_to_run:
        analyze_heavy_data(task)
    elapsed_seq = time.perf_counter() - start_seq
    print(f"{'1. Sekwencyjnie (1 rdzeń)':<25} | Czas wykonania: {elapsed_seq:.4f} s")
    
    run_benchmark("2. Wątki (ThreadPool)", ThreadPoolExecutor, tasks_to_run)
    
    run_benchmark("3. Procesy (ProcessPool)", ProcessPoolExecutor, tasks_to_run)
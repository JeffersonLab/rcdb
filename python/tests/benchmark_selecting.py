import time
import rcdb

selection = "@is_production and not @is_empty_target and cdc_gas_pressure >=99.8 and cdc_gas_pressure<=100.2"
run_min = 0
run_max = 1000000

def run_select_runs():
    db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb2")
    runs = db.select_runs(selection,run_min, run_max)

def run_select_values():
    db = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb2")
    runs = db.select_values(['polarization_angle','beam_current'], selection, run_min=run_min, run_max=run_max)
    print("   preparation      {}", runs.performance["preparation"])
    print("   query            {}", runs.performance["query"])
    print("   selection        {}", runs.performance["selection"])
    print("   total            {}", runs.performance["total"])


def benchmark_function(func, n=1):
    """
    Run the given function `n` times and measure the total and average time.
    """
    total_time = 0.0
    for i in range(n):
        start = time.time()
        func()
        end = time.time()
        elapsed = end - start
        total_time += elapsed
        print(f"Run {i+1}: {func.__name__} took {elapsed:.6f} seconds")
    avg_time = total_time / n
    print(f"Average time for {func.__name__} over {n} runs: {avg_time:.6f} seconds\n")

if __name__ == "__main__":
    # Adjust the number of runs as needed
    # benchmark_function(run_select_runs, n=5)
    benchmark_function(run_select_values, n=5)
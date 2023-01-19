import argparse
import random
import time
from rcdb import RCDBProvider, ConditionType


def print_cycle(current_index, total,  message):
    x = 1

    if current_index >= 1000000:
        x = current_index%1000000
    elif current_index >= 10000:
        x = current_index%10000
    elif current_index >= 1000:
        x = current_index%1000
    elif current_index >= 100:
        x = current_index%100
    else:
        x = current_index%10

    if not x:
        print("Progress {} of {} in {}".format(current_index, total, message))


def benchmark_conditions_add(cycles, auto_commit=True):
    # Create RCDBProvider object that connects to DB and provide most of the functions
    db = RCDBProvider("sqlite:///example.db")

    # Create condition type
    runs = [db.create_run(1), db.create_run(2)]
    ct = db.create_condition_type("my_val", ConditionType.INT_FIELD, "This is my value")

    print ("Start {} cycles in benchmark_conditions_add".format(cycles))

    # cycle
    for i in range(0, cycles):
        print_cycle(i, cycles, "benchmark_conditions_add")
        db.add_condition(random.choice(runs), ct, random.randrange(0, 1000),
                         replace=True, auto_commit=auto_commit)

    # commit in the end if needed
    if not auto_commit:
        db.session.commit()

    print ("Done benchmark_conditions_add")


if __name__ == "__main__":

    mode_help = """Benchmark modes:
    add               - usual conditions addition
    add_manual_commit - add many conditions with auto_commit=False and commit changes after
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['add', 'add_manual_commit'], help=mode_help)
    parser.add_argument("-c", "--cycles", type=int, default=1000, help="Number of repetition of benchmark action")
    args = parser.parse_args()

    start_clock = time.process_time()
    start_time = time.time()
    if args.mode == 'add':
        benchmark_conditions_add(args.cycles)
    else:
        benchmark_conditions_add(args.cycles, auto_commit=False)
    print("Approximate time using time.clock() is: {} \t time is {}"
          .format(time.process_time() - start_clock, time.time() - start_time))
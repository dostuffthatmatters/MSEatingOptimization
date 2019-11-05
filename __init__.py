from Optimization import Optimization
from Helpers.custom_printing import CustomPrinting
from time import time

import cProfile

def optimizer(input_file="Source/in.csv", output_file="Source/out.csv"):
    CustomPrinting.print_pink("\nOptimization starting now ...", bold=True, new_lines=2)

    time1 = time()
    # cProfile.run(f"result = Optimization(input_file=\"{input_file}\", output_file=\"{output_file}\").execute()", sort='time')
    result = Optimization(input_file=input_file, output_file=output_file).execute()
    timespan = round(time() - time1, 6)

    CustomPrinting.print_pink(f"Optimization finished successfully ({timespan} seconds).", bold=True)


if __name__ == "__main__":
    optimizer(input_file="Source/generic_example.csv")

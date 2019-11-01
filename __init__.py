from Optimization import Optimization
from Helpers.custom_printing import CustomPrinting
from time import time

def optimizer(input_file="Source/in.csv", output_file="Source/out.csv"):
    CustomPrinting.print_green("\nOptimization starting now ...", bold=True, new_lines=3)

    time1 = time()
    result = Optimization(input_file=input_file, output_file=output_file).execute()
    timespan = round(time() - time1, 6)

    if result[0]:
        CustomPrinting.print_green(f"Optimization finished successfully ({timespan} seconds).", bold=True)
    else:
        CustomPrinting.print_red(f"Optimization did not finish: {result[1]}", bold=True)


if __name__ == "__main__":
    optimizer(input_file="Source/generic_example.csv")

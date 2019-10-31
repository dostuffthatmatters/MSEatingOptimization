from Optimization import Optimization
from Helpers.custom_printing import CustomPrinting

def optimizer(input_file="Source/in.csv", output_file="Source/out.csv"):
    CustomPrinting.print("\nOptimization starting now ...", bold=True, new_lines=2)

    Optimization(input_file=input_file, output_file=output_file)
    result = Optimization.execute()

    if result[0]:
        CustomPrinting.print_green("\nOptimization finished successfully ...", bold=True)
    else:
        CustomPrinting.print_red(f"\nOptimization did not finish: {result[1]}", bold=True)


if __name__ == "__main__":
    optimizer(input_file="Source/example.csv")

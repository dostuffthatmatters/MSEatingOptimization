from Optimization import Optimization
from Helpers.custom_printing import CustomPrinting

def optimizer(input_file="Source/in.csv", output_file="Source/out.csv"):
    CustomPrinting.print("\nOptimization starting now ...", bold=True, new_lines=2)
    result = Optimization(input_file=input_file, output_file=output_file).execute()
    if result[0]:
        CustomPrinting.print_green("Optimization finished successfully ...", bold=True)
    else:
        CustomPrinting.print_red(f"Optimization did not finish: {result[1]}", bold=True)



if __name__ == "__main__":
    optimizer()







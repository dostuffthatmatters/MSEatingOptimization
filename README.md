## MSEating Opimization

This module is using **Python 3.7** with the dependecies as
listed in `requirements.txt`. You can install all dependencies 
by using `pip install -r requirements.txt`.

You can clone this repository and use it in two ways:
* Execute `__init__.py` itself
* Having this module(-folder) inside you projects directory 
and calling `from MSEatingOptimization import optimizer` 
followed by `optimizer()`

The data input and output is using csv-files (ex-/importable 
by Excel, Numbers, etc.). By default you have to save the input 
table as `Source/in.csv` and the output table will be generated
as `Source/out.csv`.

You can change the input and output directory by using 
`optimizer(input_file="...", output_file="...")`.
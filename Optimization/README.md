## Optimization Class



Inside **``attendee.py``** you can find the class `Guest` and `Host` that are used during the whole execution.



The class **`Optimization`** inside `__init__.py` is responsible for delegation every step of the execution lifecycle:

1. Loading Models from CSV-tables (And determining geographic coordinates), creating all `Guest`- and `Host`-instances
2. Calculating all distances (that have not been calculated yet) between all occuring geographic coordinates
3. Calling the Optimizer (which is determining each `Host`-instance’s variable `<host>.guests` and each `Guest`-instance’s variable `<guest>.host`)
4. Exporting all Models as a CSV-table
5. Exporting the optimization-result as an image



Inside the directory **`Optimizer`** you can find the actual optimizers that distribute all Guest-instances among all Host-instances.



**`csv_link.py`** is responsible for interacting with the CSV-tables (using `csv`).

**`visual_link.py`** is responsible for interacting with the CSV-tables (using `PIL`).






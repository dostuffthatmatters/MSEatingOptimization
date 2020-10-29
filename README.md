# MSEating Optimization

## Background

An optimization for the MSEating event. People can sign up for a dinner 
with other people from our university department.

They specify whether they want to host a dinner or take part in one. This 
optimization matches all guests with dinner hosts so that the overall squared
travel distance is minimized.

<br/>

## Task

Input: CSV-table from an attendee signup. Every row is representing and attendee (name, host (yes,no), max guests (if host), adress, email, etc.)

Output: CSV-table containing all matched groups. Additionaly a visualisation of the optimization result itself - Example:

![](Optimization/Optimizer/56_comparison/squared_error.png)

*Blue rings/dots are hosts (with their respective number of guests in pink numbers), green rings/dots are matched guests, red rings/dots are unmatched guests (only possible if there are simply not enough hosts).*

See a description of my optimization algorithm here: 
https://github.com/dostuffthatmatters/MSEatingOptimization/tree/master/Optimization/Optimizer

<br/>

**Annotation:** This project is actually not intended to be for public use because it is a very general problem but a really specific usecase. That's why the actual use of it as a tool is not really documented.

<br/>

## General Information

This module is using **Python 3.7** with the dependecies as listed in `requirements.txt`. You can install all dependencies by running `pip install -r requirements.txt`.

You can clone this repository and use it in two ways:
* Execute `__init__.py` itself (the one in the main directory `MSEating-Optimization`)
* Having this module(-folder) inside your projects directory and calling `from MSEatingOptimization import optimizer` followed by `optimizer()`

The data input and output is using csv-files (ex-/importable by Excel, Numbers, etc.). By default you have to save the input table as `Source/in.csv` and the output table will be generated as `Source/out.csv`.

You can change the input and output directory by using 
`optimizer(input_file="...", output_file="...")`.

**Important:**
You have to add a file `secrets.py` with the following content:

```python

GOOGLE_GEOCODING_API_KEY = "..."  # You can get this key from the Google Developer Console (or ask me)

OUTLOOK_CREDENTIALS_USER = "..."
OUTLOOK_CREDENTIALS_PASS = "..."
OUTLOOK_FROM_EMAIL = "..."

```

Google Developer Console: https://developers.google.com/maps/documentation/geocoding/get-api-key

<br/>

## Explanation of the file structure

The main optimization is stored inside the directory **`Optimization`** : See this directory for details.

<br/>

Inside the directory **`Database`** I handle all database-related logic:

* I store all geographic coordinates of zip-codes inside a database so that I don’t unnecessarily use the Google API and don't have to wait for the API at every execution.
* I also store all possible distances between stored geographical coordinates inside that database so that I don’t have to calculate this at every execution
* I only use Getter- and Setter-functions to interact with the database from outside that directory

<br/>

Inside the directory **`Helpers`** I handle all operations that are not really specific to this optimization problem:

* I wrote a wrapper `CustomLogger` for python’s `logging`-module
* I also wrote a class `CustomPrinting` to `print` in colors and bold/underlined with ease
* In my `CustomMath` class I do mathematical operation - e.g. evaluating the [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula) to determine the distance between two coordinates

<br/>

Inside the directory **`Source`** I store all files used as input parameters/created as output files:

* The background image (map of munich) of the image exported after optimization
* The image created during the optimization
* Input and Output CSV-tables

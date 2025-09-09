# proto-simkit
Rapid simulation prototyping with SimPy, DuckDB, and Streamlit.

## Introduction
Proto-SimKit is a simple toolkit for building quick simulation models.

The goal is speed: instead of spending days on a detailed setup, you can get a working prototype in front of decision makers within days. This makes it easier to test ideas, explore scenarios, and decide whether a more advanced model is worth the investment.

The framework is reusable, so you can adapt it to new processes without starting from scratch. It comes with logging, analysis, and a ready-to-use app interface, so the focus stays on experimenting and learning fast.

## Features
- 📦 simple SimPy-based discrete-event simulation modelling pickers preparing orders in a warehouse across two shifts
- 🗄️ events logging into DuckDB for dast, SQL-friendly analysis
- 📊 Streamlit app allowing users to enter the number and skills of pickers in each shift and visuliazing the performance metrics


## Installation
Clone the repository and install the required packages:
```
git clone https://github.com/Arthurbdt/proto-simkit.git
cd proto-simkit
pip install -r requirements.txt
```

## Usage
Use the command below to run the Streamlit app:
```
streamlit run app/main.py
```
Variables like orders inter-arrival times, lead times and pick times can be changed in sim/config.py.

## Warehouse model
The example model included in this project is a simplified warehouse picking process. 

Orders arrive over time and wait in a queue until a picker is available. Pickers work in shifts and have different skill levels that affect their speed. 

The simulation tracks how many orders are in the system, how pickers spend their time (working, waiting, or off-shift), and whether orders are completed on time.



# proto-simkit
Rapid simulation prototyping with SimPy, DuckDB, and Streamlit.

## Introduction
Proto-SimKit is a simple toolkit for building quick simulation models.

The goal is to get a working prototype in front of decision makers as soon as possible. This makes it easier to test ideas, explore scenarios, and decide whether a more advanced model is worth the investment.

The framework is reusable, so you can adapt it to new processes without starting from scratch. It comes with logging, analysis, and an app interface, so the focus stays on experimenting and learning fast.

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
The app will launch and the following table will appear:

![image info](/app/images/pickers_table.png)

You can add as many pickers as you want, name them, assign them a shift and seniority level. Make sure you don't leave an empty row in the table or an error will be raised when starting the simulation.

When you're ready to see the results, click on "Run simulation" in the left-hand panel.

Variables like orders inter-arrival times, lead times and pick times can be changed in sim/config.py.

## Warehouse model
The example model included in this project is a simplified warehouse picking process. 

Orders arrive over time and wait in a queue until a picker is available. Pickers work in shifts and have different skill levels that affect their speed. 

The simulation tracks how many orders are in the system, how pickers spend their time (working, waiting, or off-shift), and whether orders are completed on time.

## Results analysis

Once the simulation has run, some metrics and visualizations appear:
- Pickers workload: shows how many orders were processed by each picker (or were not picked during the simulation).

![image info](/app/images/pickers_workload.png)

- Pickers usage: shows the distribution of time spend in each state per picker.

![image info](/app/images/pickers_usage.png)

- Work in process: number of orders in the system over time. First and second shifts are shaded differently to help assess wether each shift is properly staffed.

![image info](/app/images/work_in_process.png)



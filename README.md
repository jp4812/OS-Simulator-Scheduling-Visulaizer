# OS-Simulator-Scheduling-Visulaizer
An interactive CPU Scheduling Visualizer built with Python (PyQt6). Schedulyze allows users to add processes, choose scheduling algorithms, and visualize execution using a Gantt chart.
Here’s a solid **README.md** draft for your repo that explains your project clearly and makes it easy for others (and evaluators) to understand and run it:

---
## Features
- Add processes with **Arrival Time** and **Burst Time**.
- Supports multiple scheduling algorithms:
  - **FCFS (First Come First Serve)**
  - **SJF (Shortest Job First)**
  - **Round Robin (Quantum = 2)**
- Interactive **Gantt Chart Visualization**.
- Reset functionality to clear processes and chart.
- Simple and intuitive GUI built with **PyQt6**.

---

## Project Structure
```
├── main_window.ui        # Qt Designer UI file
├── schedulyze.py         # Main application logic
├── README.md             # Documentation
```

---

## Requirements
- Python 3.9+
- PyQt6

Install dependencies:
```bash
pip install PyQt6
```

---

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/schedulyze.git
   cd schedulyze
   ```
2. Run the application:
   ```bash
   python schedulyze.py
   ```
3. Use the GUI:
   - Add processes with arrival and burst times.
   - Select an algorithm from the dropdown.
   - Click **Simulate** to generate the Gantt chart.
   - Click **Clear** to reset processes and chart.

---

## Demo
- **Process Table**: Displays all added processes.
- **Gantt Chart**: Shows execution order and timing visually.

---

## Algorithms Implemented
### FCFS
Processes are executed in the order they arrive.  
### SJF
Processes with the shortest burst time are executed first.  
### Round Robin
Processes are executed in time slices (quantum = 2).  

---

## Future Improvements
- Add **Priority Scheduling**.
- Allow user-defined **quantum** for Round Robin.
- Export results (waiting time, turnaround time) to CSV.

---

## Author
Developed by **Jemil and Veer** as part of an **Operating Systems course project**.  

---

Would you like me to also add a **“Screenshots” section with placeholders** so you can drop in images of your app UI and Gantt chart? That usually makes a README stand out more for academic projects.

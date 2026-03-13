import sys
from PyQt6 import QtWidgets, uic, QtCore

class SchedulyzeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file - ensure this matches your filename
        uic.loadUi("main_window.ui", self)
        
        self.setWindowTitle("OS-Sim: Schedulyze")
        self.processes = []
        
        # Connect Buttons
        self.btn_add.clicked.connect(self.add_process)
        self.btn_simulate.clicked.connect(self.run_simulation)
        self.btn_clear.clicked.connect(self.clear_processes)
        
        # Setup Table
        self.table_processes.setColumnCount(3)
        self.table_processes.setHorizontalHeaderLabels(["ID", "Arrival", "Burst"])
        self.table_processes.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def clear_processes(self):
        """Resets the application state entirely."""
        self.processes = []
        self.table_processes.setRowCount(0)
        
        # Clear the Gantt blocks but keep the layout structure
        if self.gantt_container.layout():
            layout = self.gantt_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        self.gantt_container.update()
        print("System Reset: All data cleared.")

    def add_process(self):
        """Adds a new process to the list and table."""
        arrival = self.spinBox.value() 
        burst = self.spin_burst.value()
        
        if burst <= 0:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Burst time must be > 0")
            return

        p_id = f"P{len(self.processes) + 1}"
        self.processes.append({"id": p_id, "arrival": arrival, "burst": burst})
        self.update_table()

    def update_table(self):
        """Syncs the internal process list with the UI table."""
        self.table_processes.setRowCount(len(self.processes))
        for i, p in enumerate(self.processes):
            self.table_processes.setItem(i, 0, QtWidgets.QTableWidgetItem(p['id']))
            self.table_processes.setItem(i, 1, QtWidgets.QTableWidgetItem(str(p['arrival'])))
            self.table_processes.setItem(i, 2, QtWidgets.QTableWidgetItem(str(p['burst'])))

    def run_simulation(self):
        """Main execution logic for the chosen algorithm."""
        if not self.processes: 
            QtWidgets.QMessageBox.warning(self, "Warning", "Please add processes first!")
            return
        
        algo = self.combo_algorithm.currentText()
        results = []

        if algo == "FCFS":
            results = self.logic_fcfs()
        elif algo == "SJF":
            results = self.logic_sjf()
        elif algo == "Round Robin":
            results = self.logic_round_robin()
        
        if results:
            self.draw_gantt(results)

    def draw_gantt(self, results):
        """Visualizes the scheduling results as colored blocks."""
        # 1. Handle Layout safely to avoid 'Layout already exists' error
        if self.gantt_container.layout() is None:
            layout = QtWidgets.QHBoxLayout(self.gantt_container)
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout = self.gantt_container.layout()
            # Clear existing blocks
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # 2. Add new blocks
        colors = ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f", "#9b59b6"]
        for i, res in enumerate(results):
            block = QtWidgets.QLabel(f"{res['id']}\n{res['start']}-{res['finish']}")
            # Adjust width multiplier (30) to make blocks larger/smaller
            block.setFixedSize(max(res['burst'] * 30, 60), 70)
            
            # Use process ID for consistent color across segments
            try:
                p_num = int(''.join(filter(str.isdigit, res['id'])))
            except:
                p_num = i
                
            color = colors[p_num % len(colors)]
            block.setStyleSheet(f"""
                background-color: {color}; 
                border: 1px solid white; 
                color: white; 
                font-weight: bold;
                font-size: 10px;
            """)
            block.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(block)
        
        layout.addStretch()
        self.gantt_container.update()

    def logic_fcfs(self):
        procs = sorted(self.processes, key=lambda x: x['arrival'])
        current_time = 0
        results = []
        for p in procs:
            if current_time < p['arrival']: 
                current_time = p['arrival']
            start = current_time
            finish = start + p['burst']
            results.append({"id": p['id'], "start": start, "finish": finish, "burst": p['burst']})
            current_time = finish
        return results

    def logic_sjf(self):
        pending = sorted(self.processes, key=lambda x: x['arrival'])
        ready = []
        current_time = 0
        results = []
        while pending or ready:
            while pending and pending[0]['arrival'] <= current_time:
                ready.append(pending.pop(0))
            if not ready:
                current_time = pending[0]['arrival']
                continue
            ready.sort(key=lambda x: x['burst'])
            p = ready.pop(0)
            start = current_time
            finish = start + p['burst']
            results.append({"id": p['id'], "start": start, "finish": finish, "burst": p['burst']})
            current_time = finish
        return results

    def logic_round_robin(self):
        quantum = 2 # In a real app, get this from a QSpinBox!
        queue = sorted(self.processes, key=lambda x: x['arrival'])
        ready_q = []
        current_time = 0
        results = []
        rem_burst = {p['id']: p['burst'] for p in self.processes}
        
        temp_queue = list(queue)
        
        while temp_queue or ready_q:
            while temp_queue and temp_queue[0]['arrival'] <= current_time:
                ready_q.append(temp_queue.pop(0))
            
            if not ready_q:
                current_time = temp_queue[0]['arrival']
                continue
                
            p = ready_q.pop(0)
            start = current_time
            take = min(rem_burst[p['id']], quantum)
            rem_burst[p['id']] -= take
            current_time += take
            results.append({"id": p['id'], "start": start, "finish": current_time, "burst": take})
            
            while temp_queue and temp_queue[0]['arrival'] <= current_time:
                ready_q.append(temp_queue.pop(0))
            
            if rem_burst[p['id']] > 0:
                ready_q.append(p)
        return results

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SchedulyzeApp()
    window.show()
    sys.exit(app.exec())
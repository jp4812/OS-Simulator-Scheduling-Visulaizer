import sys
from PyQt6 import QtWidgets, uic, QtCore

class SchedulyzeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_window.ui", self)
        
        self.setWindowTitle("OS-Sim: Schedulyze")
        self.processes = []
        
        # Connect Buttons
        self.btn_add.clicked.connect(self.add_process)
        self.btn_simulate.clicked.connect(self.run_simulation)
        self.btn_clear.clicked.connect(self.clear_processes)
        
        # Setup Table
        self.table_processes.setColumnCount(4)
        self.table_processes.setHorizontalHeaderLabels(["ID", "Arrival", "Burst", "Priority"])
        self.table_processes.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def clear_processes(self):
        """Resets the application state entirely."""
        self.processes = []
        self.table_processes.setRowCount(0)
        
        if self.gantt_container.layout():
            layout = self.gantt_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        self.gantt_container.update()
        self.label_stats.setText("Run a simulation to see metrics...")
        print("System Reset: All data cleared.")

    def add_process(self):
        """Adds a new process to the list and table."""
        arrival = self.spinBox_arrival.value() 
        burst = self.spin_burst.value()
        priority = self.spin_priority.value()
        
        if burst <= 0:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Burst time must be > 0")
            return

        p_id = f"P{len(self.processes) + 1}"
        self.processes.append({
            "id": p_id, 
            "arrival": arrival, 
            "burst": burst,
            "priority": priority
        })
        self.update_table()

    def update_table(self):
        """Syncs the internal process list with the UI table."""
        self.table_processes.setRowCount(len(self.processes))
        for i, p in enumerate(self.processes):
            self.table_processes.setItem(i, 0, QtWidgets.QTableWidgetItem(p['id']))
            self.table_processes.setItem(i, 1, QtWidgets.QTableWidgetItem(str(p['arrival'])))
            self.table_processes.setItem(i, 2, QtWidgets.QTableWidgetItem(str(p['burst'])))
            self.table_processes.setItem(i, 3, QtWidgets.QTableWidgetItem(str(p['priority'])))

    def detect_context_switches(self, results):
        """Returns a list of times where a context switch occurred."""
        switches = []
        for i in range(1, len(results)):
            if results[i]['id'] != results[i-1]['id']:
                switches.append({
                    "time": results[i]['start'],
                    "from": results[i-1]['id'],
                    "to": results[i]['id']
                })
        return switches

    def calculate_metrics(self, results):
        """Calculate average waiting time and turnaround time."""
        total_wait = 0
        total_turnaround = 0
        
        for p in self.processes:
            # Find completion time for this process
            completion_time = 0
            for res in results:
                if res['id'] == p['id']:
                    completion_time = max(completion_time, res['finish'])
            
            turnaround = completion_time - p['arrival']
            waiting = turnaround - p['burst']
            
            total_turnaround += turnaround
            total_wait += waiting
        
        avg_wait = total_wait / len(self.processes) if self.processes else 0
        avg_turnaround = total_turnaround / len(self.processes) if self.processes else 0
        
        return avg_wait, avg_turnaround

    def run_simulation(self):
        """Main execution logic for the chosen algorithm."""
        if not self.processes: 
            QtWidgets.QMessageBox.warning(self, "Warning", "Please add processes first!")
            return
        
        algo = self.combo_algorithm.currentText()
        results = []

        if "FCFS" in algo:
            results = self.logic_fcfs()
        elif "SJF" in algo:
            results = self.logic_sjf()
        elif "Round Robin" in algo:
            results = self.logic_round_robin()
        elif "Non-Preemptive" in algo:
            results = self.logic_non_preemptive_priority()
        elif "Preemptive" in algo:
            results = self.logic_preemptive_priority()
        
        if results:
            self.draw_gantt(results)

            switches = self.detect_context_switches(results)
            avg_wait, avg_turnaround = self.calculate_metrics(results)
            
            # Update statistics label
            stats_text = f"Avg Waiting Time: {avg_wait:.2f}  |  Avg Turnaround: {avg_turnaround:.2f}  |  Context Switches: {len(switches)}"
            self.label_stats.setText(stats_text)
            
            if switches:
                lines = [f"  t={s['time']:>3}: {s['from']} → {s['to']}" for s in switches]
                msg = f"{len(switches)} Context Switch(es) Detected:\n\n" + "\n".join(lines)
            else:
                msg = "No context switches occurred."

            QtWidgets.QMessageBox.information(self, "Simulation Results", msg)

    def draw_gantt(self, results):
        """Visualizes the scheduling results as colored blocks."""
        if self.gantt_container.layout() is None:
            layout = QtWidgets.QHBoxLayout(self.gantt_container)
            layout.setSpacing(1)
            layout.setContentsMargins(5, 5, 5, 5)
        else:
            layout = self.gantt_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Modern gradient colors for each process
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B88B", "#A8D8EA"
        ]
        
        for i, res in enumerate(results):
            block = QtWidgets.QLabel(f"{res['id']}\n{res['start']}-{res['finish']}")
            block.setFixedSize(max(res['burst'] * 35, 70), 80)
            
            try:
                p_num = int(''.join(filter(str.isdigit, res['id'])))
            except:
                p_num = i
                
            color = colors[p_num % len(colors)]
            block.setStyleSheet(f"""
                QLabel {{
                    background-color: {color}; 
                    border: 2px solid #ffffff; 
                    border-radius: 8px;
                    color: white; 
                    font-weight: bold;
                    font-size: 11px;
                }}
            """)
            block.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(block)
        layout.addStretch()
        self.gantt_container.update()

    def logic_fcfs(self):
        """First Come First Served"""
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
        """Shortest Job First (Non-Preemptive)"""
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
        """Round Robin with Quantum = 2"""
        quantum = 2
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
            #to check if any new process has arrived during the execution of current process
            while temp_queue and temp_queue[0]['arrival'] <= current_time:
                ready_q.append(temp_queue.pop(0))
            
            if rem_burst[p['id']] > 0:
                ready_q.append(p)
        return results

    def logic_non_preemptive_priority(self):
        """Non-Preemptive Priority Scheduling (Lower number = Higher priority)"""
        pending = sorted(self.processes, key=lambda x: x['arrival'])
        ready = []
        current_time = 0
        results = []
        
        while pending or ready:
            # Add all processes that have arrived
            while pending and pending[0]['arrival'] <= current_time:
                ready.append(pending.pop(0))
            
            if not ready:
                if pending:
                    current_time = pending[0]['arrival']
                continue
            
            # Sort by priority (lower number = higher priority)
            ready.sort(key=lambda x: x['priority'])
            p = ready.pop(0)
        
            start = current_time
            finish = start + p['burst']
            results.append({"id": p['id'], "start": start, "finish": finish, "burst": p['burst']})
            current_time = finish
        return results
    
    def logic_preemptive_priority(self):
        """Preemptive Priority Scheduling (Lower number = Higher priority)"""
        pending = sorted(self.processes, key=lambda x: x['arrival'])
        current_time = 0
        results = []
        remaining_burst = {p['id']: p['burst'] for p in self.processes}
        
        while pending or any(remaining_burst[p['id']] > 0 for p in self.processes):
            # Add all processes that have arrived at current time
            while pending and pending[0]['arrival'] <= current_time:
                pending.pop(0)
            
            # Find the process with highest priority among those in ready queue
            available = [p for p in self.processes if p['arrival'] <= current_time and remaining_burst[p['id']] > 0]
            
            if not available:
                if pending:
                    current_time = pending[0]['arrival']
                continue
            
            # Select process with highest priority (lowest priority number)
            current_process = min(available, key=lambda x: (x['priority'], x['arrival']))
            
            # Execute for 1 unit of time
            burst_time = 1
            finish_time = current_time + burst_time
            remaining_burst[current_process['id']] -= burst_time
            
            results.append({
                "id": current_process['id'], 
                "start": current_time, 
                "finish": finish_time, 
                "burst": burst_time
            })
            
            current_time = finish_time
        
        return results


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SchedulyzeApp()
    window.show()
    sys.exit(app.exec())
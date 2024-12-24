from flask import Flask, render_template, jsonify, request
from dataclasses import dataclass
from typing import List
import random

@dataclass
class Process:
    pid: int
    burst_time: int
    arrival_time: int
    remaining_time: int
    completion_time: int = 0
    waiting_time: int = 0
    turnaround_time: int = 0
    response_time: int = -1  
    color: str = ""

class RoundRobinScheduler:
    def __init__(self, processes: List[Process], time_quantum: int):
        self.processes = sorted(processes, key=lambda x: (x.arrival_time, x.pid))  
        self.time_quantum = time_quantum
        self.current_time = 0
        self.queue = []
        self.completed_processes = []
        self.execution_history = []
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', 
                 '#D4A5A5', '#9B59B6', '#3498DB', '#E74C3C', '#2ECC71']
        for i, process in enumerate(self.processes):
            process.color = colors[i % len(colors)]
    
    def run(self):
        remaining_processes = self.processes.copy()
        
        while remaining_processes or self.queue:
            arrived = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            for process in arrived:
                self.queue.append(process)
                remaining_processes.remove(process)
            
            if not self.queue:
                if remaining_processes:
                    next_arrival = min(p.arrival_time for p in remaining_processes)
                    while self.current_time < next_arrival:
                        self.execution_history.append({
                            "time": self.current_time,
                            "running": None,
                            "queue": []
                        })
                        self.current_time += 1
                    continue
                break
            
            current_process = self.queue.pop(0)
            
            if current_process.response_time == -1:
                current_process.response_time = self.current_time - current_process.arrival_time
            
            time_slice = min(self.time_quantum, current_process.remaining_time)
            
            # Execute process
            for _ in range(time_slice):
                self.execution_history.append({
                    "time": self.current_time,
                    "running": {
                        "pid": current_process.pid,
                        "remaining_time": current_process.remaining_time,
                        "color": current_process.color
                    },
                    "queue": [{
                        "pid": p.pid,
                        "remaining_time": p.remaining_time,
                        "color": p.color
                    } for p in self.queue]
                })
                
                current_process.remaining_time -= 1
                self.current_time += 1
                
                arrived = [p for p in remaining_processes if p.arrival_time <= self.current_time]
                for process in arrived:
                    self.queue.append(process)
                    remaining_processes.remove(process)
            
            if current_process.remaining_time > 0:
                self.queue.append(current_process)
            else:
                current_process.completion_time = self.current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                self.completed_processes.append(current_process)
    
    def get_statistics(self):
        if not self.completed_processes:
            return {
                "average_waiting_time": 0,
                "average_turnaround_time": 0,
                "average_response_time": 0,
                "completion_order": [],
                "process_details": []
            }
        
        avg_waiting_time = sum(p.waiting_time for p in self.completed_processes) / len(self.completed_processes)
        avg_turnaround_time = sum(p.turnaround_time for p in self.completed_processes) / len(self.completed_processes)
        avg_response_time = sum(p.response_time for p in self.completed_processes) / len(self.completed_processes)
        
        process_details = [{
            "pid": p.pid,
            "arrival_time": p.arrival_time,
            "burst_time": p.burst_time,
            "completion_time": p.completion_time,
            "turnaround_time": p.turnaround_time,
            "waiting_time": p.waiting_time,
            "response_time": p.response_time
        } for p in self.completed_processes]
        
        return {
            "average_waiting_time": round(avg_waiting_time, 2),
            "average_turnaround_time": round(avg_turnaround_time, 2),
            "average_response_time": round(avg_response_time, 2),
            "completion_order": [p.pid for p in self.completed_processes],
            "process_details": process_details
        }

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    time_quantum = int(request.form.get('timeQuantum', 3)) 
    processes = [
        Process(pid=1, burst_time=8, arrival_time=0, remaining_time=8),
        Process(pid=2, burst_time=4, arrival_time=1, remaining_time=4),
        Process(pid=3, burst_time=9, arrival_time=2, remaining_time=9),
        Process(pid=4, burst_time=5, arrival_time=3, remaining_time=5),
    ]
    
    scheduler = RoundRobinScheduler(processes, time_quantum)
    scheduler.run()
    
    return jsonify({
        "history": scheduler.execution_history,
        "statistics": scheduler.get_statistics()
    })

if __name__ == '__main__':
    app.run(debug=True)
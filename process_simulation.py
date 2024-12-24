import random
import time
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

class Process:
    def __init__(self):
        current_time = int(time.time() * 1000)
        self.id = str(current_time)
        self.time = random.randint(1, 100)
        self.active = False
        self.start_time = None
        self.finish_time = None
        self.creation_time = current_time
        print(f"{Fore.GREEN}Process spawned: Process ID: {self.id} | Time: {self.time}")

    def check_life(self) -> bool:
        if self.time <= 0:
            self.active = False
            print(f"{Fore.RED}Process killed: Process ID: {self.id}")
            self.finish_time = int(time.time() * 1000)
            return True
        return False

def validate_process_times(process):
    current_time = int(time.time() * 1000)
    if process.creation_time is None:
        process.creation_time = current_time
    if process.start_time is None:
        process.start_time = current_time
    if process.finish_time is None:
        process.finish_time = current_time
    return process

def run_simulation():
    print("\n" + "="*50)
    print(f"Simulation started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("="*50 + "\n")

    processes = []
    total_spawned = 0
    total_killed = 0
    total_cpu_active_time = 0
    quantum = 3
    current_process_index = 0
    simulation_start_time = int(time.time() * 1000)
    last_step_time = simulation_start_time

    process_events = []
    cpu_idle_intervals = []
    last_cpu_idle_start = None

    for step in range(0, 1000):
        if random.randint(0, 100) < 20:
            spawn = Process()
            processes.append(spawn)
            total_spawned += 1
            process_events.append(("spawn", spawn.id, step))

        cpu_idle = True

        if processes:
            current_process = processes[current_process_index]
            if current_process.start_time is None:
                current_process.start_time = int(time.time() * 1000)
            current_process.active = True
            cpu_idle = False

            for _ in range(min(quantum, current_process.time)):
                current_time = int(time.time() * 1000)
                
                if current_process.check_life():
                    process_events.append(("kill", current_process.id, step))
                    processes.pop(current_process_index)
                    total_killed += 1
                    if not processes:
                        break
                    if current_process_index >= len(processes):
                        current_process_index = 0
                    if processes:
                        current_process = processes[current_process_index]
                    continue

                current_process.time -= 1
                print(f"{Fore.BLUE}Process ID: {current_process.id} | Time Remaining: {current_process.time} | Status: Active | Step {step}")
                process_events.append(("execute", current_process.id, step))

            current_process.active = False
            if processes:
                current_process_index = (current_process_index + 1) % len(processes)

        if not cpu_idle:
            current_time = int(time.time() * 1000)
            total_cpu_active_time += current_time - last_step_time
            last_step_time = current_time
        else:
            print(f"{Fore.YELLOW}CPU Idle | Step: {step}")
            process_events.append(("idle", None, step))

    simulation_end_time = int(time.time() * 1000)
    processes = [validate_process_times(p) for p in processes]

    total_wait_time = 0
    total_turnaround_time = 0
    for process in processes:
        wait_time = process.start_time - process.creation_time
        total_wait_time += wait_time
        turnaround_time = process.finish_time - process.creation_time
        total_turnaround_time += turnaround_time

    total_processes = total_killed + len(processes)
    if total_processes > 0:
        avg_wait_time = total_wait_time / total_processes
        avg_turnaround_time = total_turnaround_time / total_processes
    else:
        avg_wait_time = 0
        avg_turnaround_time = 0

    simulation_duration = simulation_end_time - simulation_start_time
    cpu_utilization = (total_cpu_active_time / simulation_duration) * 100 if simulation_duration > 0 else 0

    print("\n" + "="*20 + " Simulation Summary " + "="*20)
    print(f"Remaining processes: {len(processes)}")
    print(f"Total spawned: {total_spawned}")
    print(f"Total killed: {total_killed}")
    print(f"Average Wait Time: {avg_wait_time:.2f} ms")
    print(f"Average Turnaround Time: {avg_turnaround_time:.2f} ms")
    print(f"CPU Utilization: {cpu_utilization:.2f}%")
    print(f"Simulation Duration: {simulation_duration} ms")
    print("="*59 + "\n")

    return process_events, {
        'total_spawned': total_spawned,
        'total_killed': total_killed,
        'avg_wait_time': avg_wait_time,
        'avg_turnaround_time': avg_turnaround_time,
        'cpu_utilization': cpu_utilization
    }

if __name__ == "__main__":
    run_simulation()
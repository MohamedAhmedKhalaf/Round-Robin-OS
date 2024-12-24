let processCounter = 1;
let simulationSpeed = 1000; 
let currentTime = 0;
let isSimulationRunning = false;

function getRandomColor() {
    const colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
        '#D4A5A5', '#9B59B6', '#3498DB', '#E67E22', '#2ECC71'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

document.getElementById('add-process').addEventListener('click', () => {
    const processList = document.getElementById('process-list');
    const processItem = document.createElement('div');
    processItem.className = 'process-item';
    processItem.innerHTML = `
        <span>Process ${processCounter}</span>
        <div class="input-group">
            <label>Burst Time:</label>
            <input type="number" class="burst-time" min="1" value="1">
        </div>
        <div class="input-group">
            <label>Arrival Time:</label>
            <input type="number" class="arrival-time" min="0" value="0">
        </div>
        <button onclick="this.parentElement.remove()">Remove</button>
    `;
    processList.appendChild(processItem);
    processCounter++;
});

function createProcessElement(processId, color) {
    const process = document.createElement('div');
    process.className = 'process-animation';
    process.style.backgroundColor = color;
    process.style.width = '40px';
    process.style.height = '40px';
    process.style.borderRadius = '50%';
    process.style.display = 'flex';
    process.style.alignItems = 'center';
    process.style.justifyContent = 'center';
    process.style.color = 'white';
    process.style.fontWeight = 'bold';
    process.style.margin = '10px auto';
    process.textContent = `P${processId}`;
    return process;
}

async function animateExecution(executionHistory) {
    const queueContainer = document.getElementById('process-queue');
    const cpuContainer = document.getElementById('current-process');
    const completedContainer = document.getElementById('completed-processes');
    const timeDisplay = document.getElementById('time-display');
    
    currentTime = 0;
    isSimulationRunning = true;
    
    const processColors = {};
    
    for (const execution of executionHistory) {
        if (!isSimulationRunning) break;
        
        if (!processColors[execution.process_id]) {
            processColors[execution.process_id] = getRandomColor();
        }
        
        timeDisplay.textContent = `Current Time: ${execution.start_time}`;
        
        const processElement = createProcessElement(
            execution.process_id,
            processColors[execution.process_id]
        );
        
        queueContainer.appendChild(processElement);
        await new Promise(r => setTimeout(r, simulationSpeed / 2));
        
        cpuContainer.innerHTML = '';
        cpuContainer.appendChild(processElement);
        
        
        await new Promise(r => setTimeout(r, 
            simulationSpeed * (execution.end_time - execution.start_time)));
        
        
        completedContainer.appendChild(processElement);
        
        currentTime = execution.end_time;
        timeDisplay.textContent = `Current Time: ${currentTime}`;
    }
    
    isSimulationRunning = false;
}

document.getElementById('start-simulation').addEventListener('click', async () => {
    
    document.getElementById('process-queue').innerHTML = '';
    document.getElementById('current-process').innerHTML = '';
    document.getElementById('completed-processes').innerHTML = '';
    
    const processes = [];
    document.querySelectorAll('.process-item').forEach((item, index) => {
        processes.push({
            id: index + 1,
            burst_time: parseInt(item.querySelector('.burst-time').value),
            arrival_time: parseInt(item.querySelector('.arrival-time').value)
        });
    });

    const timeQuantum = parseInt(document.getElementById('time-quantum').value);

    const response = await fetch('/simulate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            processes: processes,
            time_quantum: timeQuantum
        }),
    });

    const result = await response.json();
    
    
    animateExecution(result.execution_history);
    
 
    updateStatistics(result);
});

function updateStatistics(result) {
    document.getElementById('avg-waiting-time').textContent = 
        `Average Waiting Time: ${result.average_waiting_time.toFixed(2)}`;
    document.getElementById('avg-turnaround-time').textContent = 
        `Average Turnaround Time: ${result.average_turnaround_time.toFixed(2)}`;

    const tableBody = document.querySelector('#process-table tbody');
    tableBody.innerHTML = '';
    
    result.process_details.forEach(process => {
        const row = tableBody.insertRow();
        row.insertCell().textContent = process.id;
        row.insertCell().textContent = process.waiting_time;
        row.insertCell().textContent = process.turnaround_time;
        row.insertCell().textContent = process.completion_time;
    });
}


const speedControl = document.createElement('div');
speedControl.innerHTML = `
    <label for="simulation-speed">Simulation Speed:</label>
    <select id="simulation-speed">
        <option value="2000">Slow</option>
        <option value="1000" selected>Normal</option>
        <option value="500">Fast</option>
        <option value="250">Very Fast</option>
    </select>
`;
document.querySelector('.visualization-section').insertBefore(
    speedControl,
    document.querySelector('.simulation-container')
);

document.getElementById('simulation-speed').addEventListener('change', (e) => {
    simulationSpeed = parseInt(e.target.value);
});
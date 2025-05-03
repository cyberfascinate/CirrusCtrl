// Chart Setup
const cpuCtx = document.getElementById('cpuChart');
const memCtx = document.getElementById('memoryChart');
const uptimeCtx = document.getElementById('uptimeChart');

let cpuData = {
  labels: [],
  datasets: [{
    label: 'CPU %',
    data: [],
    borderColor: '#FF5733',
    fill: false
  }]
};

let memData = {
  labels: [],
  datasets: [{
    label: 'Memory %',
    data: [],
    borderColor: '#33C1FF',
    fill: false
  }]
};

let cpuChart = new Chart(cpuCtx, {
  type: 'line',
  data: cpuData,
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'CPU Usage (%)'
      }
    }
  }
});

let memChart = new Chart(memCtx, {
  type: 'line',
  data: memData,
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Memory Usage (%)'
      }
    }
  }
});

let uptimeChart = new Chart(uptimeCtx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'System Uptime (seconds)',
      data: [],
      borderColor: '#F39C12',
      fill: false
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Uptime (seconds)'
      }
    }
  }
});

// Output functions
function runAction(action) {
  fetch('/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ action: action })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('outputBox').textContent = formatOutput(data.output);
  })
  .catch(err => {
    console.error("Error:", err);
    alert("Failed to communicate with server.");
  });
}

function clearOutput() {
  document.getElementById('outputBox').textContent = '';
}

function formatOutput(output) {
  try {
    const parsed = JSON.parse(output);
    return JSON.stringify(parsed, null, 2);
  } catch (e) {
    return output;
  }
}

// Poll metrics every 5 seconds
function pollMetrics() {
  fetch('/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ action: 'system_summary' })
  })
  .then(res => res.json())
  .then(data => {
    const output = data.output;

    const matchCpu = output.match(/CPU Usage: ([\d\.]+)%/);
    const cpu = matchCpu ? parseFloat(matchCpu[1]) : null;

    const matchMem = output.match(/Memory Usage: ([\d\.]+)%/);
    const memory = matchMem ? parseFloat(matchMem[1]) : null;

    const matchDisk = output.match(/Disk Usage: ([\d\.]+)%/);
    const disk = matchDisk ? parseFloat(matchDisk[1]) : null;

    updateLineChart(cpuChart, cpu, "CPU %");
    updateLineChart(memChart, memory, "Memory %");

    const matchUptime = output.match(/Uptime:\s*(.*?)\n/);
    if (matchUptime) {
      const uptimeStr = matchUptime[1];
      const seconds = parseUptimeToSeconds(uptimeStr);
      updateLineChart(uptimeChart, seconds, "Uptime (sec)");
    }
  });
}

function updateLineChart(chart, value, label) {
  const now = new Date().toLocaleTimeString();
  chart.data.labels.push(now);
  chart.data.datasets[0].data.push(value);
  if (chart.data.labels.length > 10) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }
  chart.options.plugins.title.text = `${label}: ${value}`;
  chart.update();
}

function parseUptimeToSeconds(str) {
  const daysMatch = str.match(/(\d+)\s+days?/);
  const hoursMatch = str.match(/(\d+)\s+hours?/);
  const minutesMatch = str.match(/(\d+)\s+minutes?/);
  const secondsMatch = str.match(/(\d+)\s+seconds?/);

  let totalSeconds = 0;
  if (daysMatch) totalSeconds += parseInt(daysMatch[1]) * 86400;
  if (hoursMatch) totalSeconds += parseInt(hoursMatch[1]) * 3600;
  if (minutesMatch) totalSeconds += parseInt(minutesMatch[1]) * 60;
  if (secondsMatch) totalSeconds += parseInt(secondsMatch[1]);

  return totalSeconds;
}

// Log & Export
function downloadLog() {
  fetch('/download_log')
    .then(res => res.text())
    .then(data => {
      const blob = new Blob([data], { type: 'text/plain' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'system_log.txt';
      link.click();
    });
}

function filterLogs() {
  const term = document.getElementById('logFilter').value.toLowerCase();
  const lines = document.getElementById('outputBox').innerText.split('\n');
  const filtered = lines.filter(line => line.toLowerCase().includes(term)).join('\n');
  document.getElementById('outputBox').innerText = filtered;
}

// Command & Process Control
function runCustomCommand() {
  const cmd = document.getElementById('customCommand').value;
  fetch('/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ action: 'custom_cmd', command: cmd })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('outputBox').textContent = data.output;
  });
}

function killProcess() {
  const pid = document.getElementById('pidInput').value;
  fetch('/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ action: 'kill_process', pid: pid })
  }).then(res => res.json())
   .then(data => alert(data.output));
}

// Network Tools
function runNetworkTool(tool) {
  const host = document.getElementById('hostInput').value;
  fetch('/action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ action: tool, host: host })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('outputBox').textContent = data.output;
  });
}

// Remote Host
function fetchRemote() {
  const host = document.getElementById('remoteHost').value;
  fetch('/remote', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ host: host })
  }).then(res => res.json())
   .then(data => {
     document.getElementById('outputBox').textContent = JSON.stringify(data, null, 2);
   });
}

// Start polling metrics
setInterval(pollMetrics, 5000);
pollMetrics();

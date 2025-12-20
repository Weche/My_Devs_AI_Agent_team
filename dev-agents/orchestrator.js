/**
 * Agent Orchestrator - Runs all Dev Agents from a single process
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Agent configurations
const AGENTS = [
  {
    name: 'Frontend Agent',
    dir: join(__dirname, 'frontend-agent'),
    port: 3001,
    color: '\x1b[36m' // Cyan
  },
  {
    name: 'Backend Agent',
    dir: join(__dirname, 'backend-agent'),
    port: 3002,
    color: '\x1b[33m' // Yellow
  },
  {
    name: 'Database Agent',
    dir: join(__dirname, 'database-agent'),
    port: 3003,
    color: '\x1b[35m' // Magenta
  }
];

const RESET = '\x1b[0m';

console.log('\n🚀 Starting Agent Orchestrator...\n');

// Track running agents
const runningAgents = [];

// Start each agent
AGENTS.forEach(agent => {
  console.log(`${agent.color}[${agent.name}]${RESET} Starting on port ${agent.port}...`);

  const child = spawn('npm', ['run', 'dev'], {
    cwd: agent.dir,
    shell: true,
    stdio: 'pipe'
  });

  // Prefix output with agent name and color
  child.stdout.on('data', (data) => {
    const lines = data.toString().split('\n').filter(line => line.trim());
    lines.forEach(line => {
      console.log(`${agent.color}[${agent.name}]${RESET} ${line}`);
    });
  });

  child.stderr.on('data', (data) => {
    const lines = data.toString().split('\n').filter(line => line.trim());
    lines.forEach(line => {
      console.error(`${agent.color}[${agent.name}]${RESET} ${line}`);
    });
  });

  child.on('close', (code) => {
    console.log(`${agent.color}[${agent.name}]${RESET} Stopped (exit code: ${code})`);

    // Remove from running agents
    const index = runningAgents.indexOf(child);
    if (index > -1) {
      runningAgents.splice(index, 1);
    }

    // If all agents stopped, exit
    if (runningAgents.length === 0) {
      console.log('\n❌ All agents stopped. Orchestrator shutting down.\n');
      process.exit(0);
    }
  });

  runningAgents.push(child);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down all agents...\n');

  runningAgents.forEach(child => {
    child.kill('SIGTERM');
  });

  setTimeout(() => {
    console.log('✅ All agents stopped.\n');
    process.exit(0);
  }, 2000);
});

console.log('\n✅ All agents started!');
console.log('📊 Orchestrator running. Press Ctrl+C to stop all agents.\n');

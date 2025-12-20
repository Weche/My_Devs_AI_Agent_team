/**
 * Dev Agent Service - StreamUI-based code execution service
 * Communicates with Python backend via REST API
 */

import express from 'express';
import cors from 'cors';
import { DevAgent } from './agent.js';
import type { ExecuteTaskRequest, ExecuteTaskResponse } from './types.js';
// Load shared environment from root .env
import sharedEnv from '../../shared-env.js';

const app = express();
const PORT = 3003; // Database Agent port

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Dev Agent
const devAgent = new DevAgent();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Dev Agent Service',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// Main endpoint: Execute a task
app.post('/execute-task', async (req, res) => {
  const { task_id, stream }: ExecuteTaskRequest = req.body;

  if (!task_id) {
    return res.status(400).json({
      success: false,
      error: 'task_id is required',
    } as ExecuteTaskResponse);
  }

  console.log(`\n📥 Received task execution request for Task #${task_id}`);

  try {
    // Execute task with Dev Agent
    const result = await devAgent.executeTask(task_id);

    res.json(result as ExecuteTaskResponse);
  } catch (error) {
    console.error('Error in /execute-task:', error);

    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Internal server error',
    } as ExecuteTaskResponse);
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Dev Agent Service running on http://localhost:${PORT}`);
  console.log(`   Health check: http://localhost:${PORT}/health`);
  console.log(`   Execute task: POST http://localhost:${PORT}/execute-task`);
  console.log(`\n   Waiting for task execution requests from Albedo...\n`);
});

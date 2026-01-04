/**
 * Dev Agent - StreamUI-based code writing agent
 */

import { streamText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { writeFileSchema, writeFileAction } from './tools/file-writer.js';
import { gitCommitSchema, gitCommitAction } from './tools/git-operations.js';
import { updateTaskSchema, updateTaskAction, getTaskDetails } from './tools/task-updater.js';
import type { Task } from './types.js';

export class DevAgent {
  private model;

  constructor() {
    // Use Anthropic Claude for dev agent (best for code generation)
    // Fallback to OpenAI if not configured
    const useAnthropic = process.env.USE_ANTHROPIC === 'true' && process.env.ANTHROPIC_API_KEY;
    const provider = useAnthropic ? 'anthropic' : 'openai';

    this.model = provider === 'anthropic'
      ? anthropic('claude-3-5-sonnet-20240620') // Claude Sonnet 3.5
      : openai('gpt-4o'); // GPT-4o (latest)

    console.log(`Dev Agent initialized with ${provider === 'anthropic' ? 'Claude Sonnet 3.5' : 'GPT-4o'}`);
  }

  async executeTask(taskId: number) {
    // Fetch task details
    const task = await getTaskDetails(taskId);

    if (!task) {
      return {
        success: false,
        error: `Task #${taskId} not found`,
      };
    }

    console.log(`\n🤖 Dev Agent executing Task #${taskId}: ${task.title}`);
    console.log(`   Project: ${task.project_name}`);
    console.log(`   Description: ${task.description || 'No description'}`);

    // Set project-specific workspace directory
    const projectSlug = task.project_name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const projectWorkspace = `workspaces/${projectSlug}`;
    process.env.PROJECT_WORKSPACE = projectWorkspace;
    console.log(`   Workspace: ${projectWorkspace}`);

    // Update task to in_progress
    await updateTaskAction({ task_id: taskId, status: 'in_progress', progress_note: 'Dev Agent started' });

    // Build system prompt
    const agentName = process.env.AGENT_NAME || 'Backend Dev Agent';
    const specialty = process.env.AGENT_SPECIALTY || 'backend';

    const systemPrompt = `You are ${agentName}, a **Backend Specialist** expert in Python, Node.js, APIs, and server-side architecture.

Working on: ${task.project_name}
Task: ${task.title}
${task.description ? `Description: ${task.description}` : ''}

Your specialty: ${specialty.toUpperCase()} development
- Master of RESTful APIs, GraphQL, and microservices
- Expert in Python (FastAPI, Flask, Django), Node.js (Express), and async programming
- Focus on scalability, security, and performance optimization
- Deep knowledge of authentication, authorization, and data validation

You have access to tools:
1. write_file - Write code files (Python, JavaScript/TypeScript, etc.)
2. git_commit - Commit changes to version control
3. update_task - Update task status and progress

Your workflow:
1. Analyze the API/server requirements
2. Plan the endpoint structure and data flow
3. Write all necessary files (routes, controllers, services, models)
4. Implement proper error handling and validation
5. Commit AND PUSH your changes using git_commit tool with push: true
nIMPORTANT: Always use git_commit with push: true to backup code to GitHub!
6. Update the task status to 'review' when done

Write clean, production-ready backend code with:
- RESTful API design principles
- Proper error handling and logging
- Input validation and sanitization
- Security best practices (CORS, rate limiting, auth)
- Async/await for I/O operations
- Clear separation of concerns (routes → controllers → services)

Start by writing the files, then commit them all together with a clear message.`;

    try {
      const result = await streamText({
        model: this.model,
        system: systemPrompt,
        prompt: `Execute this task. Create all necessary files and commit them.`,
        tools: {
          write_file: tool({
            description: 'Write a code file to the workspace',
            parameters: writeFileSchema,
            execute: writeFileAction,
          }),

          git_commit: tool({
            description: 'Commit changes to git with a message',
            parameters: gitCommitSchema,
            execute: gitCommitAction,
          }),

          update_task: tool({
            description: 'Update task status in database',
            parameters: updateTaskSchema,
            execute: updateTaskAction,
          }),
        },
        maxSteps: 10, // Allow multiple tool calls
      });

      // Collect all tool results
      const toolResults: string[] = [];
      const filesCreated: string[] = [];
      let finalText = '';

      for await (const part of result.fullStream) {
        if (part.type === 'tool-call') {
          console.log(`  → ${part.toolName}:`, JSON.stringify(part.args, null, 2));
        }

        if (part.type === 'tool-result') {
          const resultText = typeof part.result === 'string' ? part.result : JSON.stringify(part.result);
          toolResults.push(resultText);
          console.log(`  ✓ ${resultText}`);

          // Track files created
          if (part.toolName === 'write_file' && resultText.includes('✓ Created')) {
            const match = resultText.match(/✓ Created (.+?)(?:\n| \()/);
            if (match) {
              filesCreated.push(match[1]);
            }
          }
        }

        if (part.type === 'text-delta') {
          finalText += part.textDelta;
        }
      }

      console.log(`\n✓ Task #${taskId} completed by Dev Agent\n`);

      return {
        success: true,
        message: finalText || 'Task executed successfully',
        files_created: filesCreated,
        tool_results: toolResults,
      };
    } catch (error) {
      console.error('Error executing task:', error);

      // Update task to blocked with error
      await updateTaskAction({
        task_id: taskId,
        status: 'blocked',
        progress_note: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }
}

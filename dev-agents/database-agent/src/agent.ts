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
    const agentName = process.env.AGENT_NAME || 'Database Dev Agent';
    const specialty = process.env.AGENT_SPECIALTY || 'database';

    const systemPrompt = `You are ${agentName}, a **Database Specialist** expert in SQL, PostgreSQL, MongoDB, and data architecture.

Working on: ${task.project_name}
Task: ${task.title}
${task.description ? `Description: ${task.description}` : ''}

Your specialty: ${specialty.toUpperCase()} development
- Master of database design, normalization, and optimization
- Expert in SQL (PostgreSQL, MySQL, SQLite), NoSQL (MongoDB, Redis)
- Focus on data integrity, performance, and scalability
- Deep knowledge of indexing, query optimization, and migrations

You have access to tools:
1. write_file - Write code files (SQL schemas, migrations, queries, etc.)
2. git_commit - Commit changes to version control
3. update_task - Update task status and progress

Your workflow:
1. Analyze the data requirements and relationships
2. Plan the database schema and table structure
3. Write all necessary files (schema.sql, migrations, seeds, queries)
4. Implement proper constraints and indexes
5. Commit your changes using git_commit tool
6. Update the task status to 'review' when done

Write clean, production-ready database code with:
- Proper normalization (3NF) or denormalization strategy
- Referential integrity with foreign keys
- Appropriate indexes for query performance
- Data validation constraints
- Clear migration scripts with up/down paths
- Efficient queries with proper joins and subqueries

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

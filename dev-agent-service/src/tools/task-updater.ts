/**
 * Task Updater Tool - Updates task status in Python database
 */

import Database from 'better-sqlite3';
import { join } from 'path';
import { z } from 'zod';

export const updateTaskSchema = z.object({
  task_id: z.number().describe('Task ID to update'),
  status: z.enum(['todo', 'in_progress', 'blocked', 'review', 'done']).describe('New task status'),
  progress_note: z.string().optional().describe('Optional note about progress made'),
});

export type UpdateTaskParams = z.infer<typeof updateTaskSchema>;

export async function updateTaskAction(params: UpdateTaskParams): Promise<string> {
  const { task_id, status, progress_note } = params;

  const dbPath = process.env.DATABASE_PATH || join(process.cwd(), '../data/database/pm_system.db');

  try {
    const db = new Database(dbPath);

    // Update task status
    const stmt = db.prepare(`
      UPDATE tasks
      SET status = ?, updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    const result = stmt.run(status, task_id);

    if (result.changes === 0) {
      db.close();
      return `✗ Task #${task_id} not found`;
    }

    // If moving to 'done', set completed_at
    if (status === 'done') {
      const completeStmt = db.prepare(`
        UPDATE tasks
        SET completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `);
      completeStmt.run(task_id);
    }

    // Log progress note if provided
    if (progress_note) {
      // This would ideally call Python API to log interaction
      // For now, we'll just include it in the response
    }

    db.close();

    let response = `✓ Task #${task_id} → ${status}`;
    if (progress_note) {
      response += `\n  Note: ${progress_note}`;
    }

    return response;
  } catch (error) {
    return `✗ Failed to update task: ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}

export async function getTaskDetails(taskId: number) {
  const dbPath = process.env.DATABASE_PATH || join(process.cwd(), '../data/database/pm_system.db');

  try {
    const db = new Database(dbPath);

    const task = db.prepare(`
      SELECT t.*, p.name as project_name
      FROM tasks t
      JOIN projects p ON t.project_id = p.id
      WHERE t.id = ?
    `).get(taskId);

    db.close();

    return task || null;
  } catch (error) {
    console.error('Error fetching task:', error);
    return null;
  }
}

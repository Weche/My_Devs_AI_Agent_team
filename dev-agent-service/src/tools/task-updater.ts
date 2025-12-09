/**
 * Task Updater Tool - Updates task status in Python database
 */

import sqlite3 from 'sqlite3';
import { join } from 'path';
import { z } from 'zod';

export const updateTaskSchema = z.object({
  task_id: z.number().describe('Task ID to update'),
  status: z.enum(['todo', 'in_progress', 'blocked', 'review', 'done']).describe('New task status'),
  progress_note: z.string().optional().describe('Optional note about progress made'),
});

export type UpdateTaskParams = z.infer<typeof updateTaskSchema>;

function runQuery(db: sqlite3.Database, query: string, params: any[]): Promise<any> {
  return new Promise((resolve, reject) => {
    db.run(query, params, function(err) {
      if (err) reject(err);
      else resolve({ changes: this.changes });
    });
  });
}

function getQuery(db: sqlite3.Database, query: string, params: any[]): Promise<any> {
  return new Promise((resolve, reject) => {
    db.get(query, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

export async function updateTaskAction(params: UpdateTaskParams): Promise<string> {
  const { task_id, status, progress_note } = params;

  const dbPath = process.env.DATABASE_PATH || join(process.cwd(), '../data/database/pm_system.db');

  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(dbPath, async (err) => {
      if (err) {
        resolve(`✗ Failed to connect to database: ${err.message}`);
        return;
      }

      try {
        // Update task status
        const result = await runQuery(db, `
          UPDATE tasks
          SET status = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ?
        `, [status, task_id]);

        if (result.changes === 0) {
          db.close();
          resolve(`✗ Task #${task_id} not found`);
          return;
        }

        // If moving to 'done', set completed_at
        if (status === 'done') {
          await runQuery(db, `
            UPDATE tasks
            SET completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
          `, [task_id]);
        }

        db.close();

        let response = `✓ Task #${task_id} → ${status}`;
        if (progress_note) {
          response += `\n  Note: ${progress_note}`;
        }

        resolve(response);
      } catch (error) {
        db.close();
        resolve(`✗ Failed to update task: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    });
  });
}

export async function getTaskDetails(taskId: number): Promise<any> {
  const dbPath = process.env.DATABASE_PATH || join(process.cwd(), '../data/database/pm_system.db');

  return new Promise((resolve) => {
    const db = new sqlite3.Database(dbPath, async (err) => {
      if (err) {
        console.error('Error connecting to database:', err);
        resolve(null);
        return;
      }

      try {
        const task = await getQuery(db, `
          SELECT t.*, p.name as project_name
          FROM tasks t
          JOIN projects p ON t.project_id = p.id
          WHERE t.id = ?
        `, [taskId]);

        db.close();
        resolve(task || null);
      } catch (error) {
        console.error('Error fetching task:', error);
        db.close();
        resolve(null);
      }
    });
  });
}

/**
 * Type definitions for Dev Agent Service
 */

export interface Task {
  id: number;
  project_id: number;
  title: string;
  description: string | null;
  status: 'todo' | 'in_progress' | 'blocked' | 'review' | 'done';
  priority: 'critical' | 'high' | 'medium' | 'low';
  assigned_to: string | null;
  created_by: string | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  status: string;
  priority: number;
}

export interface ExecuteTaskRequest {
  task_id: number;
  stream?: boolean;
}

export interface ExecuteTaskResponse {
  success: boolean;
  message: string;
  files_created?: string[];
  commits?: string[];
  error?: string;
}

export interface ToolResult {
  tool: string;
  result: string;
  success: boolean;
}

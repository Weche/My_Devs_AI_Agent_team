/**
 * File Writer Tool - Writes code files to workspace
 */

import { writeFile, mkdir } from 'fs/promises';
import { dirname, join } from 'path';
import { z } from 'zod';

export const writeFileSchema = z.object({
  path: z.string().describe('File path relative to workspace root (e.g., "src/index.html")'),
  content: z.string().describe('File content to write'),
  description: z.string().optional().describe('Brief description of what this file does'),
});

export type WriteFileParams = z.infer<typeof writeFileSchema>;

export async function writeFileAction(params: WriteFileParams): Promise<string> {
  const { path, content, description } = params;

  const workspaceDir = process.env.WORKSPACE_DIR || join(process.cwd(), '../workspace');
  const fullPath = join(workspaceDir, path);

  try {
    // Ensure directory exists
    await mkdir(dirname(fullPath), { recursive: true });

    // Write file
    await writeFile(fullPath, content, 'utf-8');

    const descText = description ? ` (${description})` : '';
    return `✓ Created ${path}${descText}\n${content.split('\n').length} lines written`;
  } catch (error) {
    return `✗ Failed to write ${path}: ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}

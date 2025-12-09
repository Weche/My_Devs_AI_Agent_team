/**
 * Git Operations Tool - Commits and pushes code to GitHub
 */

import simpleGit, { SimpleGit } from 'simple-git';
import { join } from 'path';
import { z } from 'zod';

export const gitCommitSchema = z.object({
  message: z.string().describe('Commit message describing the changes'),
  files: z.array(z.string()).optional().describe('Specific files to commit (default: all changes)'),
  push: z.boolean().default(false).describe('Whether to push to remote after commit'),
});

export type GitCommitParams = z.infer<typeof gitCommitSchema>;

export async function gitCommitAction(params: GitCommitParams): Promise<string> {
  const { message, files, push } = params;

  const workspaceDir = process.env.WORKSPACE_DIR || join(process.cwd(), '../workspace');
  const git: SimpleGit = simpleGit(workspaceDir);

  try {
    // Check if git repo exists
    const isRepo = await git.checkIsRepo();
    if (!isRepo) {
      // Initialize git repo
      await git.init();
      await git.addConfig('user.name', 'Dev Agent');
      await git.addConfig('user.email', 'dev-agent@my-devs-ai.com');

      // Add remote if configured
      const githubUser = process.env.GITHUB_USER;
      const githubToken = process.env.GITHUB_TOKEN;
      if (githubUser && githubToken) {
        const repoName = workspaceDir.split('/').pop() || 'code';
        await git.addRemote(
          'origin',
          `https://${githubToken}@github.com/${githubUser}/${repoName}.git`
        );
      }
    }

    // Add files
    if (files && files.length > 0) {
      await git.add(files);
    } else {
      await git.add('.');
    }

    // Commit
    const commitResult = await git.commit(message);

    let result = `✓ Committed: "${message}"\n`;
    result += `  Files changed: ${commitResult.summary.changes}\n`;
    result += `  Insertions: +${commitResult.summary.insertions}\n`;
    result += `  Deletions: -${commitResult.summary.deletions}`;

    // Push if requested
    if (push) {
      try {
        await git.push('origin', 'main');
        result += '\n✓ Pushed to GitHub';
      } catch (pushError) {
        result += `\n⚠ Push failed: ${pushError instanceof Error ? pushError.message : 'Unknown error'}`;
      }
    }

    return result;
  } catch (error) {
    return `✗ Git operation failed: ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}

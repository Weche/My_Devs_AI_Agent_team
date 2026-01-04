/**
 * Type declarations for shared-env.js
 */

export interface SharedEnv {
  OPENAI_API_KEY: string | undefined;
  ANTHROPIC_API_KEY: string | undefined;
  GITHUB_TOKEN: string | undefined;
  GITHUB_USER: string | undefined;
  DATABASE_PATH: string;
  WORKSPACE_DIR: string;
}

declare const sharedEnv: SharedEnv;
export default sharedEnv;

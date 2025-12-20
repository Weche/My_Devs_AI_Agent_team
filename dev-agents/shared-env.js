/**
 * Shared Environment Loader
 *
 * Loads environment variables from the root .env file
 * so all agents can share the same API keys and configuration.
 *
 * This avoids duplicating .env files in each agent directory.
 */

import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load root .env file (one level up from dev-agents/)
const rootEnvPath = join(__dirname, '..', '.env');
config({ path: rootEnvPath });

// Validate required environment variables
const requiredVars = ['OPENAI_API_KEY'];
const missingVars = requiredVars.filter(v => !process.env[v]);

if (missingVars.length > 0) {
  console.error(`❌ Missing required environment variables: ${missingVars.join(', ')}`);
  console.error(`   Please add them to: ${rootEnvPath}`);
  process.exit(1);
}

console.log('✅ Environment loaded from root .env');
console.log(`   OpenAI API Key: ${process.env.OPENAI_API_KEY?.substring(0, 20)}...`);
if (process.env.ANTHROPIC_API_KEY) {
  console.log(`   Anthropic API Key: ${process.env.ANTHROPIC_API_KEY?.substring(0, 20)}...`);
}
if (process.env.GITHUB_TOKEN) {
  console.log(`   GitHub Token: ${process.env.GITHUB_TOKEN?.substring(0, 15)}...`);
}

export default {
  OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
  GITHUB_TOKEN: process.env.GITHUB_TOKEN,
  GITHUB_USER: process.env.GITHUB_USER,
  DATABASE_PATH: process.env.DATABASE_PATH || join(__dirname, '..', 'data', 'database', 'pm_system.db'),
  WORKSPACE_DIR: process.env.WORKSPACE_DIR || join(__dirname, '..', 'workspaces'),
};

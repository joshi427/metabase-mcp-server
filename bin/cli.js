#!/usr/bin/env node

/**
 * Metabase MCP Server CLI
 * This script allows running the Metabase MCP server via npx
 */

const spawn = require('cross-spawn');
const path = require('path');
const fs = require('fs');

// Get the project root directory
const projectRoot = path.resolve(__dirname, '..');

// Load environment variables from .env file
const dotenvPath = path.join(projectRoot, '.env');
let envVars = {};

if (fs.existsSync(dotenvPath)) {
  console.log('\x1b[36mLoading environment variables from .env file\x1b[0m');
  const envContent = fs.readFileSync(dotenvPath, 'utf8');
  envContent.split('\n').forEach(line => {
    // Skip empty lines and comments
    if (line.trim() === '' || line.trim().startsWith('#')) return;
    
    const [key, ...valueParts] = line.split('=');
    const value = valueParts.join('='); // Handle values that might contain '='
    
    if (key && value) {
      envVars[key.trim()] = value.trim();
      // Also set in process.env for the current process
      process.env[key.trim()] = value.trim();
    }
  });
}

// Check for required environment variables
const requiredEnvVars = ['METABASE_URL', 'METABASE_USERNAME', 'METABASE_PASSWORD'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('\x1b[31mError: Missing required environment variables:\x1b[0m');
  missingVars.forEach(varName => {
    console.error(`  - ${varName}`);
  });
  console.error('\nPlease set these variables in your .env file or environment.');
  process.exit(1);
}

console.log('\x1b[36mStarting Metabase MCP Server...\x1b[0m');
console.log(`Connecting to Metabase at: ${process.env.METABASE_URL}`);

// Run the Python server
const pythonProcess = spawn('python', ['server.py'], {
  cwd: projectRoot,
  stdio: 'inherit',
  env: process.env
});

pythonProcess.on('error', (err) => {
  console.error('\x1b[31mFailed to start Python process:\x1b[0m', err.message);
  process.exit(1);
});

pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.error(`\x1b[31mPython process exited with code ${code}\x1b[0m`);
    process.exit(code);
  }
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n\x1b[33mShutting down Metabase MCP Server...\x1b[0m');
  pythonProcess.kill('SIGINT');
});

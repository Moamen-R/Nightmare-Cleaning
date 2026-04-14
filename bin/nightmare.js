#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if Python is installed
const pythonExec = process.platform === 'win32' ? 'python' : 'python3';

const args = process.argv.slice(2);
const modulePath = path.join(__dirname, '..', 'nightmare_cleaner', 'cli.py');

// Spawning python using the module path
const child = spawn(pythonExec, [modulePath, ...args], {
    stdio: 'inherit',
    env: process.env // preserve environment
});

child.on('close', (code) => {
    process.exit(code);
});

child.on('error', (err) => {
    console.error(`Failed to start subprocess: ${ err }`);
    console.error('Do you have Python installed and added to your SYSTEM PATH?');
    process.exit(1);
});

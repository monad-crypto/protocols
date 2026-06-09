// Assembles the publishable npm package under dist/.

import { cpSync, mkdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'dist');

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

// Generated aggregates -> JS-package-friendly names
const aggregates = {
  'protocols-mainnet.json': 'mainnet.json',
  'protocols-testnet.json': 'testnet.json',
  'protocols-mainnet.csv': 'mainnet.csv',
  'protocols-testnet.csv': 'testnet.csv',
};
for (const [src, dest] of Object.entries(aggregates)) {
  cpSync(join(root, src), join(dist, dest));
}

// Files shipped under their existing names.
for (const f of ['categories.json', 'index.js', 'index.d.ts', 'package.json', 'README.md']) {
  cpSync(join(root, f), join(dist, f));
}

// Per-protocol directories, copied verbatim (casing preserved).
for (const dir of ['mainnet', 'testnet']) {
  cpSync(join(root, dir), join(dist, dir), { recursive: true });
}

console.log('Built dist/ npm package');

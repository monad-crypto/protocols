'use strict';

/**
 * Aggregated Monad protocol data, bundled from the monad-crypto/protocols
 * repository. The individual per-protocol files are also shipped in this
 * package and can be imported directly, e.g.:
 *
 *   const protocols = require('@monad-crypto/protocols');
 *   protocols.mainnet['0x'];
 *
 *   // or a single raw file (per-protocol casing is preserved):
 *   const kuru = require('@monad-crypto/protocols/mainnet/kuru.jsonc');
 *
 * CSV summaries are shipped as files too and can be resolved via:
 *   require.resolve('@monad-crypto/protocols/mainnet.csv');
 *
 * NOTE: the aggregate files referenced below are produced at bundle time by
 * scripts/build-npm.mjs (the in-repo sources are protocols-{mainnet,testnet}.json).
 * Run `npm run build` before requiring this file outside the published package.
 */

const mainnet = require('./mainnet.json');
const testnet = require('./testnet.json');
const categories = require('./categories.json');

module.exports = {
  mainnet,
  testnet,
  categories,
};

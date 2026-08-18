/**
 * A category::sub-category pair, e.g. "DeFi::DEX".
 */
export type Category = string;

/**
 * A single protocol entry, keyed by its slug in the aggregate maps.
 */
export interface Protocol {
  /** Display name of the protocol. */
  name: string;
  /** Human-readable description. */
  description: string;
  /** Whether the protocol is live, when present in the source data. */
  live?: boolean;
  /** Category::sub-category pairs, primary first. */
  categories: Category[];
  /** Mapping of contract name -> address. */
  addresses: Record<string, string>;
  /** Mapping of link type (project, twitter, github, docs, ...) -> URL. */
  links: Record<string, string>;
}

/** Map of protocol slug -> protocol entry. */
export type ProtocolMap = Record<string, Protocol>;

/** Mainnet protocols, keyed by slug. */
export declare const mainnet: ProtocolMap;

/** Testnet protocols, keyed by slug. */
export declare const testnet: ProtocolMap;

/** The full list of valid category::sub-category values. */
export declare const categories: { categories: Category[] };

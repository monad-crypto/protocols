# Protocols

This repository maintains contract addresses and links for each protocol on the Monad network to
assist with ecosystem coordination.

Representatives of each protocol should open pull requests to add or adjust their corresponding
metadata file as details change.

Please refer to [Tooling and Infrastructure](https://docs.monad.xyz/tooling-and-infra/) for
a list of infra providers supporting Monad.


## Form of entries

Each protocol has its own json file in `{testnet,mainnet}/PROTOCOL.json`. Comments are allowed,
following the [JSONC standard](https://jsonc.org/), in which case please create a `.jsonc` file.

The key fields are:
- `name`: Name of protocol.
- `description`: Description of protocol.
- `categories`: Categorization of the protocol as list of category::sub-category pairs, in order
  of closest, most general, match to furthest matching categories.
  * see the categorization section below to see available categories.
  * one category/sub-category pair is enough in most cases, however some protocols are associated
    with multiple categories.
- `addresses`: A named mapping between contract concept and address.
- `links`: Any links you are willing to provide (typically `project`, `twitter`, `github`, and
  `docs`)

Here is an example of a file describing a protocol:
```json
{
    "name": "Protocol Name",
    "description": "Protocol description",
    "categories": [
        "Gaming::Games",
        "Gaming::Mobile-First"
    ],
    "addresses": {
        "Data": "0xd9f184B2086d508f94e1aefe11dFABbcD810aeF9",
        "Avatar": "0x78925Ce372c918011Eb2966264b668B2F256224C",
        "Prop": "0x138b7CEaBC3D37a317B837EcF74320432a3A47A2",
        "Weapon": "0x865640F8e435D394519581afA81Ba7135DF668d2"
    },
    "links": {
        "project": "https://www.foo.ai/",
        "twitter": "https://x.com/bar",
        "github": "https://github.com/foo",
        "docs": "https://docs.foo.ai/"
    }
}

```
## How to submit a change

Changes are done on branches and submitted as PRs. Here is a walkthrough of the process:

### Create and switch to a new branch

```
git checkout -b your-protocol/your-branch-name
```

### Make changes and push

Once you have made the desired changes, push to the repository:
```
git push origin your-protocol/your-branch-name
```

### Create a pull request

1. Navigate to your branch on GitHub
   * You'll usually see a banner suggesting to create a PR for your recently pushed branch
2. Click "Compare & pull request" or go to the "Pull requests" tab and click "New pull request"
3. Select your branch as the source and the target branch (`main`)
4. Fill in the PR title and description
5. Add reviewer(s)
   * check below for the list of Monad Foundation reviewers 
6. Click "Create pull request"

Note that there are `GitHub Workflow rules` that verify that:
- JSON is valid
- required fields are populated
- categories are valid
- addresses have a valid format

Please ensure your submission is passing before requesting a review.


## Categories

The list of choices for the `category` field appears in `categories.json` and is also listed below.
For mental clarity, categories are organized by top-level sectors.

Generally protocols will be associated with a single category, however more than one is
permissible, in which case please put the primary category first.

- AI
  * AI::Agent Launchpad
  * AI::Abstraction Infrastructure
  * AI::Consumer AI
  * AI::Data
  * AI::Compute
  * AI::Inference
  * AI::Gaming
  * AI::Infrastructure
  * AI::Investing
  * AI::Models
  * AI::Trading Agent
  * AI::Other
- CeFi
  * CeFi::CEX
  * CeFi::Institutional Trading
  * CeFi::Other
- Consumer
  * Consumer::Betting
  * Consumer::E-commerce / Ticketing
  * Consumer::Prediction Market
  * Consumer::Social
  * Consumer::Other
- DeFi
  * DeFi::Asset Allocators
  * DeFi::Asset Issuers
  * DeFi::CDP
  * DeFi::Cross Chain
  * DeFi::DEX
  * DeFi::DEX Aggregator
  * DeFi::Indexes
  * DeFi::Insurance
  * DeFi::Intents
  * DeFi::Launchpads
  * DeFi::Lending
  * DeFi::Leveraged Farming
  * DeFi::Liquid Staking
  * DeFi::Memecoin
  * DeFi::MEV
  * DeFi::Options
  * DeFi::Perpetuals / Derivatives
  * DeFi::Prime Brokerage
  * DeFi::Reserve Currency
  * DeFi::RWA
  * DeFi::Stablecoin
  * DeFi::Stableswap
  * DeFi::Staking
  * DeFi::Synthetics
  * DeFi::Trading Interfaces
  * DeFi::Uncollateralized Lending
  * DeFi::Yield
  * DeFi::Yield Aggregator
  * DeFi::Other
- DePIN
  * DePIN::Spatial Intelligence
  * DePIN::CDN
  * DePIN::Compute
  * DePIN::Data Collection
  * DePIN::Data Labelling
  * DePIN::Mapping
  * DePIN::Monitoring Networks
  * DePIN::Storage
  * DePIN::Wireless Network
  * DePIN::Other
- DeSci
  * DeSci::Other
- Gaming
  * Gaming::Metaverse
  * Gaming::Mobile-First
  * Gaming::Games
  * Gaming::Infrastructure
  * Gaming::Other
- Governance
  * Governance::Delegation
  * Governance::Risk Management
  * Governance::Other
- Infra
  * Infra::AA
  * Infra::Automation
  * Infra::Analytics
  * Infra::Developer Tooling
  * Infra::Identity
  * Infra::Indexing
  * Infra::Interoperability
  * Infra::Gaming
  * Infra::Oracle
  * Infra::Privacy / Encryption
  * Infra::RaaS (Rollup as a Service)
  * Infra::RPC
  * Infra::WaaS
  * Infra::Wallet
  * Infra::ZK
  * Infra::Other
- NFT
  * NFT::Collections
  * NFT::Infrastructure
  * NFT::Interoperability
  * NFT::Marketplace
  * NFT::NFTFi
  * NFT::Other
- Payments
  * Payments::Credit Cards
  * Payments::Onramp and Offramps
  * Payments::Neobanks
  * Payments::Orchestration
  * Payments::Remittance
  * Payments::Other

  
## Monad Foundation Reviewers

1. [`79jke`](https://github.com/79jke)
2. [`kkqzhou`](https://github.com/kkqzhou)
3. [`therealharpaljadeja`](https://github.com/therealharpaljadeja)
4. [`portdeveloper`](https://github.com/portdeveloper)

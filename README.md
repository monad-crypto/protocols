# Protocols

This repository maintains contract addresses and links for each protocol on the Monad network to
assist with ecosystem coordination.

Representatives of each protocol should open pull requests to add or adjust their corresponding
metadata file as details change.

## Contributing

Please create a fork of this repository in your own github account (personal or company), push your changes to that fork, and then make a pull request from that fork which contributes back to monad-crypto/protocols:main.

Please make best efforts to verify your contracts on https://monadvision.com/ where possible, and let us know if you are running into issues with contract verification.

## Data

For each network (`mainnet`, `testnet`), there is one json per protocol.

Additionally, a summary csv is generated per network automatically.

* Mainnet: [summary csv](https://raw.githubusercontent.com/monad-crypto/protocols/refs/heads/main/protocols-mainnet.csv) | [individual protocols](https://github.com/monad-crypto/protocols/tree/main/mainnet)
* Testnet: [summary csv](https://raw.githubusercontent.com/monad-crypto/protocols/refs/heads/main/protocols-testnet.csv) | [individual protocols](https://github.com/monad-crypto/protocols/tree/main/testnet)

For a list of infra providers supporting Monad, see [Docs -> Tooling and Infrastructure](https://docs.monad.xyz/tooling-and-infra/).

## Protocol format

Each protocol has its own json file in `{testnet,mainnet}/PROTOCOL.json`. Comments are allowed,
following the [JSONC standard](https://jsonc.org/), in which case please create a `.jsonc` file instead of a `.json` file.

The fields are:
- `name`: Name of protocol (**required**)
- `description`: Description of protocol (**required**)
- `categories`: Categorization of the protocol as a list of category::sub-category pairs, in order
  of closest to furthest matching categories (**required**)
  * see the categorization section below to see available categories.
  * one category/sub-category pair is enough in most cases, however multiple are allowed
- `addresses`: A mapping between contract names and addresses (**required**, but you may specify
  an empty mapping to avoid triggering validation errors)
- `links`: Any links you are willing to provide (typically `project`, `twitter`, `github`, and
  `docs`) (**required**, but you may specify
  an empty mapping to avoid triggering validation errors)

Here is an example of a file:
```json
{
    "name": "Protocol Name",
    "description": "Protocol description",
    "categories": [
        "Gaming::Games",
        "Gaming::Mobile-First"
    ],
    "addresses": {
        "CharacterFactory": "0xd9f184B2086d508f94e1aefe11dFABbcD810aeF9",
        "AvatarFactory": "0x78925Ce372c918011Eb2966264b668B2F256224C"
    },
    "links": {
        "project": "https://www.foo.ai/",
        "twitter": "https://x.com/bar",
        "github": "https://github.com/foo",
        "docs": "https://docs.foo.ai/"
    }
}
```

## Validation

### Validating your entry

Before submitting your entry, please run validation locally:

```
# assuming your file was mainnet/PROTOCOL_NAME.{json,jsonc}
python scripts/validate_protocol.py --network mainnet --protocol PROTOCOL_NAME
```

### Validating all jsons

The following will be run on each commit:

```
python scripts/validate_protocol.py --network testnet
python scripts/validate_protocol.py --network mainnet
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

The list of choices for the `category` field appears in [`categories.json`](categories.json) and
is also listed below. For ease of understanding, categories are organized by top-level sectors.

Generally protocols will be associated with a single category, however more than one is 
permissible, in which case please put the primary category first.

<details>
<summary>AI</summary>

- `AI::Agent Launchpad`
- `AI::Abstraction Infrastructure`
- `AI::Consumer AI`
- `AI::Data`
- `AI::Compute`
- `AI::Inference`
- `AI::Gaming`
- `AI::Infrastructure`
- `AI::Investing`
- `AI::Models`
- `AI::Trading Agent`
- `AI::Other`
</details>

<details>
<summary>CeFi</summary>

- `CeFi::CEX`
- `CeFi::Institutional Trading`
- `CeFi::Other`
</details>

<details>
<summary>Consumer</summary>

- `Consumer::Betting`
- `Consumer::E-commerce / Ticketing`
- `Consumer::Prediction Market`
- `Consumer::Social`
- `Consumer::Other`
</details>

<details>
<summary>DeFi</summary>

- `DeFi::Asset Allocators`
- `DeFi::Asset Issuers`
- `DeFi::CDP`
- `DeFi::Cross Chain`
- `DeFi::DEX`
- `DeFi::DEX Aggregator`
- `DeFi::Indexes`
- `DeFi::Insurance`
- `DeFi::Intents`
- `DeFi::Launchpads`
- `DeFi::Lending`
- `DeFi::Leveraged Farming`
- `DeFi::Liquid Staking`
- `DeFi::Memecoin`
- `DeFi::MEV`
- `DeFi::Options`
- `DeFi::Perpetuals / Derivatives`
- `DeFi::Prime Brokerage`
- `DeFi::Reserve Currency`
- `DeFi::RWA`
- `DeFi::Stablecoin`
- `DeFi::Stableswap`
- `DeFi::Staking`
- `DeFi::Synthetics`
- `DeFi::Trading Interfaces`
- `DeFi::Uncollateralized Lending`
- `DeFi::Yield`
- `DeFi::Yield Aggregator`
- `DeFi::Other`
</details>

<details>
<summary>DePIN</summary>

- `DePIN::Spatial Intelligence`
- `DePIN::CDN`
- `DePIN::Compute`
- `DePIN::Data Collection`
- `DePIN::Data Labelling`
- `DePIN::Mapping`
- `DePIN::Monitoring Networks`
- `DePIN::Storage`
- `DePIN::Wireless Network`
- `DePIN::Other`
</details>

<details>
<summary>DeSci</summary>

- `DeSci::Other`
</details>

<details>
<summary>Gaming</summary>

- `Gaming::Metaverse`
- `Gaming::Mobile-First`
- `Gaming::Games`
- `Gaming::Infrastructure`
- `Gaming::Other`
</details>

<details>
<summary>Governance</summary>

- `Governance::Delegation`
- `Governance::Risk Management`
- `Governance::Other`
</details>

<details>
<summary>Infra</summary>

- `Infra::AA`
- `Infra::Automation`
- `Infra::Analytics`
- `Infra::Developer Tooling`
- `Infra::Identity`
- `Infra::Indexing`
- `Infra::Interoperability`
- `Infra::Gaming`
- `Infra::Oracle`
- `Infra::Privacy / Encryption`
- `Infra::RaaS (Rollup as a Service)`
- `Infra::RPC`
- `Infra::WaaS`
- `Infra::Wallet`
- `Infra::ZK`
- `Infra::Other`
</details>

<details>
<summary>NFT</summary>

- `NFT::Collections`
- `NFT::Infrastructure`
- `NFT::Interoperability`
- `NFT::Marketplace`
- `NFT::NFTFi`
- `NFT::Other`
</details>

<details>
<summary>Payments</summary>

- `Payments::Credit Cards`
- `Payments::Onramp and Offramps`
- `Payments::Neobanks`
- `Payments::Orchestration`
- `Payments::Remittance`
- `Payments::Other`
</details>

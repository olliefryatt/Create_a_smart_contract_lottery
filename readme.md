
Objective
1. Users can enter lottery with ETH based on a USD fee
2. An admin will determine when the lottery is over
3. The lottery will select a random winner


Start
• 6:12:00
• >> brownie init

(1) Start with lottery.sol contract

(2) Test lottery sol
• 6:23:47
• Need to check set up of smart contract
• Need to change mainnet fork out of Infura, to slow. First check where it is listed to
• 1) Delete the exsisting mainnet fork, as it's linked in Infura
• $ brownie networks delete mainnet-fork
• 2) Add are own mainnet with Alcamy
• $ brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 fork=https://eth-mainnet.alchemyapi.io/v2/dJVCKvb88ikgPR0B8rRMCKkVINyIl1HF accounts=10 mnemonic=brownie port=8545

(3) Update Lottery.sol with minimum payment
• 6:30

(4) Update only owner with a random number, using Chainlink
• 6:40:00
• https://docs.chain.link/docs/chainlink-vrf/

(5) Compile final contract 
• 7:07:00

(6) Deploy smart contract
• 7:08:00
• brownie run scripts/deploy_lottery.py
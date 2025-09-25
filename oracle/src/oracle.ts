import { ethers } from "ethers";
import axios from "axios";

// Load environment variables (inline instead of using dotenv package)
const loadEnv = () => {
    const fs = require('fs');
    const path = require('path');
    try {
        const envPath = path.join(__dirname, '../.env');
        const envFile = fs.readFileSync(envPath, 'utf8');
        envFile.split('\n').forEach((line: string) => {
            const [key, value] = line.split('=');
            if (key && value) {
                process.env[key.trim()] = value.trim();
            }
        });
    } catch (error) {
        // .env file doesn't exist, use environment variables or defaults
    }
};

// Contract ABI for IncentiveContract (matching src/ version)
const INCENTIVE_CONTRACT_ABI = [
    "function stake(uint128 _amount) external",
    "function updateScores(address _contributor, bool _isCorrect) external",
    "function claimRewards() external",
    "function setOracle(address _oracle) external",
    "function contributors(address) external view returns (uint128 amountStaked, int128 score, uint64 lastClaimTimestamp, bool isStaked)",
    "function oracle() external view returns (address)",
    "function owner() external view returns (address)"
];

async function main() {
    loadEnv();
    
    // Normalize RPC URL: convert ws:// -> http:// and wss:// -> https://
    const rawRpc = process.env.RPC_URL || "http://127.0.0.1:8545";
    let rpcUrl = rawRpc.trim();
    if (rpcUrl.startsWith("ws://")) {
        console.warn(`Normalizing RPC_URL from ws:// to http:// (was: ${rpcUrl})`);
        rpcUrl = "http://" + rpcUrl.slice(5);
    } else if (rpcUrl.startsWith("wss://")) {
        console.warn(`Normalizing RPC_URL from wss:// to https:// (was: ${rpcUrl})`);
        rpcUrl = "https://" + rpcUrl.slice(6);
    }
    
    console.log(`Using RPC URL: ${rpcUrl}`);
    
    const provider = new ethers.JsonRpcProvider(rpcUrl);
    const privateKey = process.env.ORACLE_PRIVATE_KEY!;
    const signer = new ethers.Wallet(privateKey, provider);

    const incentiveContractAddress = process.env.INCENTIVE_CONTRACT_ADDRESS;
    if (!incentiveContractAddress) {
        throw new Error("INCENTIVE_CONTRACT_ADDRESS not set in environment variables");
    }
    
    const incentiveContract = new ethers.Contract(
        incentiveContractAddress,
        INCENTIVE_CONTRACT_ABI,
        signer
    );

    // 1. Simulate fetching a new transaction and its features
    const transactionFeatures = { /*... feature data ... */ };
    // Use a valid local test account from anvil as the contributor address
    const contributorAddress = process.env.CONTRIBUTOR_ADDRESS || "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";

    // 2. Query the off-chain ML service via API (with fallback)
    let isIllicit: boolean;
    try {
        const response = await axios.post("http://127.0.0.1:8000/predict", transactionFeatures, { timeout: 5000 });
        isIllicit = response.data && response.data.prediction === 1;
        console.log("ML prediction received:", response.data);
    } catch (err: any) {
        // If the ML service isn't running, fall back to a safe default so the oracle
        // can still demonstrate submitting on-chain data without failing.
        console.warn("⚠️ ML service unreachable (http://127.0.0.1:8000). Using fallback prediction.", err && err.message ? err.message : err);
        // Fallback: treat as non-illicit by default (change if you prefer otherwise)
        isIllicit = false;
    }

    // 3. Submit the result to the smart contract
    console.log(`Submitting prediction for contributor ${contributorAddress}: isIllicit=${isIllicit}`);
    // Call updateScores with the prediction result
    const tx = await incentiveContract.updateScores(contributorAddress, !isIllicit); // !isIllicit = isCorrect
    await tx.wait();
    console.log("Transaction confirmed:", tx.hash);
}

main().catch(console.error);
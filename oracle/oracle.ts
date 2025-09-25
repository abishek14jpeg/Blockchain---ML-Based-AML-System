
import { ethers } from "ethers";
import * as fs from "fs";

// Configuration - explicitly use HTTP (never WebSocket)
const CONFIG = {
    rpcUrl: "http://localhost:8545", // Force HTTP, never ws://
    privateKey: "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80", // Anvil default
    manifestRegistryAddress: "0x5FbDB2315678afecb367f032d93F642f64180aa3", // Update after deployment
    incentiveContractAddress: "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", // Update after deployment
    adaptiveEnsembleAddress: "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0" // Update after deployment
};

// Contract ABIs (minimal for demonstration)
const MANIFEST_REGISTRY_ABI = [
    "function submitModel(bytes32 modelHash, string calldata metadata) external",
    "function getModel(uint256 index) external view returns (bytes32, address, uint256, string memory)",
    "function totalModels() external view returns (uint256)"
];

const INCENTIVE_CONTRACT_ABI = [
    "function reward(address user, uint256 rewardAmount) external payable",
    "function stakes(address user) external view returns (uint256, uint256, bool)"
];

const ADAPTIVE_ENSEMBLE_ABI = [
    "function setWeight(bytes32 modelHash, uint256 weight) external",
    "function getWeight(bytes32 modelHash) external view returns (uint256)"
];

async function loadPredictionData(): Promise<any> {
    try {
        const data = fs.readFileSync("../ml/predictions.json", "utf8");
        return JSON.parse(data);
    } catch (error) {
        console.error("Error loading predictions.json:", error);
        // Return sample data for demonstration
        return {
            modelHash: "0x" + "a".repeat(64),
            metadata: "Sample-Model-v1",
            accuracy: 0.85,
            f1_score: 0.82
        };
    }
}

async function submitModel() {
    console.log("🚀 Starting Oracle Operations...");
    
    try {
        // Setup provider and wallet
        const provider = new ethers.JsonRpcProvider(CONFIG.rpcUrl);
        const wallet = new ethers.Wallet(CONFIG.privateKey, provider);
        
        // Test connection
        const network = await provider.getNetwork();
        console.log(`Connected to network: ${network.name} (${network.chainId})`);
        
        // Load prediction data
        const predictionData = await loadPredictionData();
        console.log("📊 Loaded prediction data:", predictionData);
        
        // Connect to ManifestRegistry
        const manifestRegistry = new ethers.Contract(
            CONFIG.manifestRegistryAddress,
            MANIFEST_REGISTRY_ABI,
            wallet
        );
        
        // Submit model
        console.log("📝 Submitting model to ManifestRegistry...");
        const tx = await manifestRegistry.submitModel(
            predictionData.modelHash,
            predictionData.metadata
        );
        
        console.log("⏳ Transaction submitted:", tx.hash);
        await tx.wait();
        console.log("✅ Model submission confirmed");
        
        // Optional: Set weight in adaptive ensemble if available
        try {
            const adaptiveEnsemble = new ethers.Contract(
                CONFIG.adaptiveEnsembleAddress,
                ADAPTIVE_ENSEMBLE_ABI,
                wallet
            );
            
            // Calculate weight based on accuracy (example: accuracy * 100)
            const weight = Math.floor((predictionData.accuracy || 0.5) * 100);
            
            console.log(`⚖️ Setting model weight: ${weight}`);
            const weightTx = await adaptiveEnsemble.setWeight(
                predictionData.modelHash,
                weight
            );
            
            await weightTx.wait();
            console.log("✅ Model weight set successfully");
            
        } catch (error: any) {
            console.warn("⚠️ Could not set model weight:", error.message);
        }
        
        console.log("🎉 Oracle operations completed successfully!");
        
    } catch (error: any) {
        console.error("❌ Oracle error:", error);
        if (error.code === 'NETWORK_ERROR') {
            console.log("💡 Tip: Make sure a local Ethereum node (anvil) is running on localhost:8545");
        }
        if (error.reason) {
            console.log("Reason:", error.reason);
        }
        process.exit(1);
    }
}

// Add graceful error handling
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

export { submitModel };

// Run if called directly
if (require.main === module) {
    submitModel().catch(console.error);
}
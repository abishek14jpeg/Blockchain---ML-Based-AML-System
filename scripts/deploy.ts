
import { ethers } from "hardhat";

async function main() {
	const [deployer] = await ethers.getSigners();
	console.log("Deploying contracts with the account:", deployer.address);

	const ManifestRegistry = await ethers.getContractFactory("src/ManifestRegistry.sol:ManifestRegistry");
	const manifestRegistry = await ManifestRegistry.deploy();
	await manifestRegistry.waitForDeployment();
	console.log("ManifestRegistry deployed to:", await manifestRegistry.getAddress());

	const IncentiveContract = await ethers.getContractFactory("src/IncentiveContract.sol:IncentiveContract");
	const incentiveContract = await IncentiveContract.deploy();
	await incentiveContract.waitForDeployment();
	console.log("IncentiveContract deployed to:", await incentiveContract.getAddress());

	// Set oracle address to the deployer for demo purposes
	const oracleAddress = deployer.address;
	await incentiveContract.setOracle(oracleAddress);
	console.log("Oracle set to:", oracleAddress);
}

main().catch((error) => {
	console.error(error);
	process.exitCode = 1;
});

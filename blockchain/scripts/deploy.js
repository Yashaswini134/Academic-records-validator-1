const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
    console.log("=".repeat(70));
    console.log("DEPLOYING CERTIFICATE REGISTRY CONTRACT");
    console.log("=".repeat(70));

    // Get the contract factory
    const CertificateRegistry = await hre.ethers.getContractFactory("CertificateRegistry");

    console.log("\nDeploying contract...");

    // Deploy the contract
    const certificateRegistry = await CertificateRegistry.deploy();

    await certificateRegistry.waitForDeployment();

    const contractAddress = await certificateRegistry.getAddress();

    console.log(`✓ Contract deployed to: ${contractAddress}`);

    // Get deployer account
    const [deployer] = await hre.ethers.getSigners();
    console.log(`✓ Deployed by: ${deployer.address}`);

    // Save deployment info
    const deploymentInfo = {
        contractAddress: contractAddress,
        deployer: deployer.address,
        network: hre.network.name,
        timestamp: new Date().toISOString()
    };

    const deploymentPath = path.join(__dirname, "..", "deployment.json");
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));

    console.log(`✓ Deployment info saved to: deployment.json`);

    // Save contract ABI
    const artifactPath = path.join(
        __dirname,
        "..",
        "artifacts",
        "contracts",
        "CertificateRegistry.sol",
        "CertificateRegistry.json"
    );

    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
    const abiPath = path.join(__dirname, "..", "contract_abi.json");
    fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));

    console.log(`✓ Contract ABI saved to: contract_abi.json`);

    console.log("\n" + "=".repeat(70));
    console.log("DEPLOYMENT SUCCESSFUL");
    console.log("=".repeat(70));
    console.log("\nNext steps:");
    console.log("1. Keep the Hardhat node running");
    console.log("2. Update backend/.env with contract address");
    console.log("3. Run the backend server");
    console.log("=".repeat(70));
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });

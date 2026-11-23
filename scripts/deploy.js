const fs = require("fs");
const path = require("path");

async function main() {
  const DeviceRegistry = await ethers.getContractFactory("DeviceRegistry");
  const EvidenceAnchor = await ethers.getContractFactory("EvidenceAnchor");
  const IncidentManager = await ethers.getContractFactory("IncidentManager");
  const ChainOfCustody = await ethers.getContractFactory("ChainOfCustody");

  const deviceRegistry = await DeviceRegistry.deploy(); await deviceRegistry.waitForDeployment();
  const evidenceAnchor = await EvidenceAnchor.deploy(); await evidenceAnchor.waitForDeployment();
  const incidentManager = await IncidentManager.deploy(); await incidentManager.waitForDeployment();
  const chainOfCustody = await ChainOfCustody.deploy(); await chainOfCustody.waitForDeployment();

  const addresses = {
    DeviceRegistry: await deviceRegistry.getAddress(),
    EvidenceAnchor: await evidenceAnchor.getAddress(),
    IncidentManager: await incidentManager.getAddress(),
    ChainOfCustody: await chainOfCustody.getAddress()
  };
  fs.mkdirSync(path.join("results", "blockchain"), {recursive: true});
  fs.writeFileSync(path.join("results", "blockchain", "deployed_contracts.json"), JSON.stringify(addresses, null, 2));
  console.log(addresses);
}
main().catch((error) => { console.error(error); process.exitCode = 1; });

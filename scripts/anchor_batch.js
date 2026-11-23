const fs = require("fs");
const path = require("path");

function bytes32FromString(s) {
  return ethers.keccak256(ethers.toUtf8Bytes(s));
}

async function main() {
  const payloadPath = path.join("results", "blockchain", "payloads", "anchor_payload.json");
  const deployedPath = path.join("results", "blockchain", "deployed_contracts.json");
  if (!fs.existsSync(payloadPath)) throw new Error("Run backend/main.py first to generate anchor_payload.json");
  if (!fs.existsSync(deployedPath)) throw new Error("Run npm run deploy first");
  const payload = JSON.parse(fs.readFileSync(payloadPath));
  const deployed = JSON.parse(fs.readFileSync(deployedPath));
  const anchor = await ethers.getContractAt("EvidenceAnchor", deployed.EvidenceAnchor);
  const batchId = bytes32FromString(payload.batch_id);
  const tx = await anchor.anchorBatch(batchId, payload.merkle_root, payload.evidence_count, payload.offchain_hash);
  const receipt = await tx.wait();
  const out = {
    anchored: true,
    status: "ANCHORED_ON_LOCAL_HARDHAT",
    batch_id: payload.batch_id,
    transaction_hash: receipt.hash,
    block_number: receipt.blockNumber,
    gas_used: receipt.gasUsed.toString(),
    contract_address: deployed.EvidenceAnchor
  };
  fs.mkdirSync(path.join("results", "blockchain", "receipts"), {recursive: true});
  fs.writeFileSync(path.join("results", "blockchain", "receipts", "anchor_receipt.json"), JSON.stringify(out, null, 2));
  console.log(out);
}
main().catch((error) => { console.error(error); process.exitCode = 1; });

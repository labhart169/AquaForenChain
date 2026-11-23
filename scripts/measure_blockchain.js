const fs = require("fs");
const path = require("path");

async function main() {
  const results = {
    deployment: [],
    anchoring: null,
    verification: null,
    timestamp: new Date().toISOString(),
    measurement_scope: "local Hardhat EVM; client-observed receipt latency",
    cost_note: "USD values are fixed-parameter scenarios, not observed public-network fees"
  };

  // ---- Deploy all 4 contracts and measure gas ----
  const contracts = ["DeviceRegistry", "EvidenceAnchor", "IncidentManager", "ChainOfCustody"];
  const deployed = {};
  
  for (const name of contracts) {
    const Factory = await ethers.getContractFactory(name);
    const t0 = performance.now();
    const contract = await Factory.deploy();
    await contract.waitForDeployment();
    const t1 = performance.now();
    
    const address = await contract.getAddress();
    const deployTx = contract.deploymentTransaction();
    const receipt = await deployTx.wait();
    
    const entry = {
      contract: name,
      address: address,
      gas_used: Number(receipt.gasUsed),
      block_number: receipt.blockNumber,
      transaction_hash: receipt.hash,
      deploy_latency_ms: parseFloat((t1 - t0).toFixed(3))
    };
    results.deployment.push(entry);
    deployed[name] = { contract, address };
    console.log(`  Deployed ${name}: gas=${entry.gas_used}, latency=${entry.deploy_latency_ms}ms`);
  }

  // ---- Anchor the actual Python-generated payload and measure gas ----
  const anchor = deployed["EvidenceAnchor"].contract;
  const payloadPath = path.join("results", "blockchain", "payloads", "anchor_payload.json");
  if (!fs.existsSync(payloadPath)) {
    throw new Error("Missing anchor_payload.json. Run: python run_enhanced_experiment.py first.");
  }
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  const batchId = ethers.keccak256(ethers.toUtf8Bytes(payload.batch_id));
  const merkleRoot = payload.merkle_root;
  const offchainHash = payload.offchain_hash;
  const evidenceCount = Number(payload.evidence_count);

  const t2 = performance.now();
  const anchorTx = await anchor.anchorBatch(batchId, merkleRoot, evidenceCount, offchainHash);
  const anchorReceipt = await anchorTx.wait();
  const t3 = performance.now();

  results.anchoring = {
    gas_used: Number(anchorReceipt.gasUsed),
    block_number: anchorReceipt.blockNumber,
    transaction_hash: anchorReceipt.hash,
    latency_ms: parseFloat((t3 - t2).toFixed(3)),
    evidence_count: evidenceCount,
    batch_id: payload.batch_id,
    merkle_root: payload.merkle_root,
    offchain_hash: payload.offchain_hash
  };
  console.log(`  Anchored batch: gas=${results.anchoring.gas_used}, latency=${results.anchoring.latency_ms}ms`);

  // ---- Verify the batch (read-only, no gas) ----
  const t4 = performance.now();
  const verified = await anchor.verifyBatch(batchId, merkleRoot);
  const t5 = performance.now();

  results.verification = {
    verified: verified,
    latency_ms: parseFloat((t5 - t4).toFixed(3))
  };
  console.log(`  Verified: ${verified}, latency=${results.verification.latency_ms}ms`);

  // ---- Compute gas cost estimates at different gas prices ----
  const anchorGas = results.anchoring.gas_used;
  const totalDeployGas = results.deployment.reduce((s, d) => s + d.gas_used, 0);
  const gasPrices = [5, 10, 15, 30, 50]; // Gwei
  const ethPriceUsd = 3450;

  results.cost_estimates = gasPrices.map(gwei => {
    const anchorCostEth = (anchorGas * gwei * 1e-9);
    const deployCostEth = (totalDeployGas * gwei * 1e-9);
    return {
      gas_price_gwei: gwei,
      anchor_cost_eth: parseFloat(anchorCostEth.toFixed(8)),
      anchor_cost_usd: parseFloat((anchorCostEth * ethPriceUsd).toFixed(4)),
      deploy_cost_eth: parseFloat(deployCostEth.toFixed(8)),
      deploy_cost_usd: parseFloat((deployCostEth * ethPriceUsd).toFixed(4)),
      per_event_usd: parseFloat((anchorCostEth * ethPriceUsd / evidenceCount).toFixed(8))
    };
  });

  // ---- Save JSON results ----
  const outDir = path.join("results", "blockchain");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "blockchain_measurement.json"), JSON.stringify(results, null, 2));

  // ---- Save CSV ----
  const csvDir = path.join("results", "csv");
  fs.mkdirSync(csvDir, { recursive: true });

  // Deployment costs CSV
  let csv = "contract,address,gas_used,block_number,deploy_latency_ms\n";
  for (const d of results.deployment) {
    csv += `${d.contract},${d.address},${d.gas_used},${d.block_number},${d.deploy_latency_ms}\n`;
  }
  csv += `TOTAL_DEPLOY,,${totalDeployGas},,\n`;
  csv += `anchorBatch(5000 events),,${anchorGas},,${results.anchoring.latency_ms}\n`;
  csv += `verifyBatch(read-only),,,0,${results.verification.latency_ms}\n`;
  fs.writeFileSync(path.join(csvDir, "blockchain_measurement.csv"), csv);

  // Gas cost estimation CSV
  let costCsv = "gas_price_gwei,anchor_gas,anchor_cost_eth,anchor_cost_usd,deploy_gas,deploy_cost_usd,per_event_usd\n";
  for (const c of results.cost_estimates) {
    costCsv += `${c.gas_price_gwei},${anchorGas},${c.anchor_cost_eth},${c.anchor_cost_usd},${totalDeployGas},${c.deploy_cost_usd},${c.per_event_usd}\n`;
  }
  fs.writeFileSync(path.join(csvDir, "blockchain_gas_costs.csv"), costCsv);

  // ---- Save LaTeX table ----
  const latexDir = path.join("results", "latex");
  fs.mkdirSync(latexDir, { recursive: true });

  let latex = `% Auto-generated from Hardhat local measurement (${results.timestamp})
\\begin{table}[ht]
\\centering
\\caption{Measured Blockchain Gas Costs (Hardhat Local Node)}
\\label{tab:blockchain-measurement}
\\begin{tabular}{lrrr}
\\toprule
Operation & Gas Used & Latency (ms) & Cost @ 15\\,Gwei (USD) \\\\
\\midrule
`;
  for (const d of results.deployment) {
    const costUsd = (d.gas_used * 15 * 1e-9 * ethPriceUsd).toFixed(2);
    latex += `Deploy ${d.contract} & ${d.gas_used.toLocaleString()} & ${d.deploy_latency_ms} & \\$${costUsd} \\\\\n`;
  }
  const totalDeployCost = (totalDeployGas * 15 * 1e-9 * ethPriceUsd).toFixed(2);
  const anchorCost = (anchorGas * 15 * 1e-9 * ethPriceUsd).toFixed(2);
  const perEventCost = (anchorGas * 15 * 1e-9 * ethPriceUsd / evidenceCount).toFixed(6);

  latex += `\\midrule
\\textbf{Total deployment} & \\textbf{${totalDeployGas.toLocaleString()}} & -- & \\textbf{\\$${totalDeployCost}} \\\\
\\midrule
anchorBatch (${evidenceCount} events) & ${anchorGas.toLocaleString()} & ${results.anchoring.latency_ms} & \\$${anchorCost} \\\\
verifyBatch (read-only) & 0 & ${results.verification.latency_ms} & \\$0.00 \\\\
\\midrule
\\textbf{Per-event anchor cost} & -- & -- & \\textbf{\\$${perEventCost}} \\\\
\\bottomrule
\\end{tabular}
\\vspace{2pt}
{\\scriptsize Gas prices: 15\\,Gwei base fee, ETH/USD\\,=\\,\\$3\\,450. Local Hardhat node measurement.}
\\end{table}
`;
  fs.writeFileSync(path.join(latexDir, "table_blockchain_measurement.tex"), latex);

  console.log("\n=== Measurement Summary ===");
  console.log(`Total deploy gas: ${totalDeployGas}`);
  console.log(`Anchor gas (5000 events): ${anchorGas}`);
  console.log(`Anchor cost @ 15 Gwei: $${anchorCost}`);
  console.log(`Per-event cost: $${perEventCost}`);
  console.log(`Verify latency: ${results.verification.latency_ms}ms`);
  console.log(`Files saved to results/blockchain/, results/csv/, results/latex/`);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });

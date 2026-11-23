const { expect } = require("chai");

describe("EvidenceAnchor", function () {
  it("anchors a batch and verifies the root", async function () {
    const EvidenceAnchor = await ethers.getContractFactory("EvidenceAnchor");
    const anchor = await EvidenceAnchor.deploy();
    await anchor.waitForDeployment();
    const batchId = ethers.keccak256(ethers.toUtf8Bytes("BATCH-1"));
    const root = ethers.keccak256(ethers.toUtf8Bytes("root"));
    const offchain = ethers.keccak256(ethers.toUtf8Bytes("offchain"));
    await anchor.anchorBatch(batchId, root, 10, offchain);
    expect(await anchor.verifyBatch(batchId, root)).to.equal(true);
  });
});

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract EvidenceAnchor {
    struct BatchCommitment {
        bytes32 merkleRoot;
        bytes32 offchainHash;
        uint256 evidenceCount;
        uint256 timestamp;
        address submitter;
        bool exists;
    }

    mapping(bytes32 => BatchCommitment) public batches;
    bytes32[] public batchIds;

    event EvidenceBatchAnchored(
        bytes32 indexed batchId,
        bytes32 indexed merkleRoot,
        bytes32 offchainHash,
        uint256 evidenceCount,
        address indexed submitter
    );

    function anchorBatch(bytes32 batchId, bytes32 merkleRoot, uint256 evidenceCount, bytes32 offchainHash) external {
        require(!batches[batchId].exists, "batch already anchored");
        require(evidenceCount > 0, "empty batch");
        batches[batchId] = BatchCommitment(merkleRoot, offchainHash, evidenceCount, block.timestamp, msg.sender, true);
        batchIds.push(batchId);
        emit EvidenceBatchAnchored(batchId, merkleRoot, offchainHash, evidenceCount, msg.sender);
    }

    function verifyBatch(bytes32 batchId, bytes32 merkleRoot) external view returns (bool) {
        return batches[batchId].exists && batches[batchId].merkleRoot == merkleRoot;
    }

    function getBatchCount() external view returns (uint256) {
        return batchIds.length;
    }
}

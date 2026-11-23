// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ChainOfCustody {
    struct CustodyAction {
        bytes32 evidenceId;
        bytes32 actionHash;
        string actionType;
        address actor;
        uint256 timestamp;
    }

    CustodyAction[] public actions;
    event CustodyActionRecorded(bytes32 indexed evidenceId, bytes32 indexed actionHash, string actionType, address indexed actor);

    function recordAction(bytes32 evidenceId, bytes32 actionHash, string calldata actionType) external {
        actions.push(CustodyAction(evidenceId, actionHash, actionType, msg.sender, block.timestamp));
        emit CustodyActionRecorded(evidenceId, actionHash, actionType, msg.sender);
    }

    function getActionCount() external view returns (uint256) {
        return actions.length;
    }
}

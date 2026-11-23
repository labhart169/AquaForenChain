// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract IncidentManager {
    struct Incident {
        uint256 id;
        bytes32 batchId;
        string incidentType;
        string severity;
        uint256 openedAt;
        bool closed;
    }

    uint256 public nextIncidentId = 1;
    mapping(uint256 => Incident) public incidents;

    event IncidentCreated(uint256 indexed id, bytes32 indexed batchId, string incidentType, string severity);
    event IncidentClosed(uint256 indexed id);

    function createIncident(bytes32 batchId, string calldata incidentType, string calldata severity) external returns (uint256) {
        uint256 id = nextIncidentId++;
        incidents[id] = Incident(id, batchId, incidentType, severity, block.timestamp, false);
        emit IncidentCreated(id, batchId, incidentType, severity);
        return id;
    }

    function closeIncident(uint256 id) external {
        require(incidents[id].id != 0, "unknown incident");
        incidents[id].closed = true;
        emit IncidentClosed(id);
    }
}

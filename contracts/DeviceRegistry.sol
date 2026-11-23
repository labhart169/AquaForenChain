// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract DeviceRegistry {
    address public admin;
    mapping(bytes32 => bool) public authorizedDevices;
    mapping(bytes32 => string) public deviceTypes;

    event DeviceRegistered(bytes32 indexed deviceId, string deviceType);
    event DeviceRevoked(bytes32 indexed deviceId);

    modifier onlyAdmin() {
        require(msg.sender == admin, "not admin");
        _;
    }

    constructor() { admin = msg.sender; }

    function registerDevice(bytes32 deviceId, string calldata deviceType) external onlyAdmin {
        authorizedDevices[deviceId] = true;
        deviceTypes[deviceId] = deviceType;
        emit DeviceRegistered(deviceId, deviceType);
    }

    function revokeDevice(bytes32 deviceId) external onlyAdmin {
        authorizedDevices[deviceId] = false;
        emit DeviceRevoked(deviceId);
    }

    function isAuthorized(bytes32 deviceId) external view returns (bool) {
        return authorizedDevices[deviceId];
    }
}

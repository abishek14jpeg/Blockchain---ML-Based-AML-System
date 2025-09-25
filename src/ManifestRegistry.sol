// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ManifestRegistry {
    // Mapping from a contributor's address to a list of their submitted model hashes
    mapping(address => bytes32[]) public modelHashesByContributor;

    // Event to announce the registration of a new model
    event ModelRegistered(address indexed contributor, bytes32 modelHash);

    /**
     * @dev Registers a new model hash for the message sender.
     * @param _modelHash The keccak256 hash of the off-chain model artifacts.
     */
    function registerModel(bytes32 _modelHash) external {
        modelHashesByContributor[msg.sender].push(_modelHash);
        emit ModelRegistered(msg.sender, _modelHash);
    }
}

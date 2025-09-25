// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ManifestRegistry {
    struct Model {
        bytes32 modelHash;
        address contributor;
        uint256 timestamp;
        string metadata;
    }

    Model[] public models;
    mapping(bytes32 => bool) public hashExists;

    event ModelSubmitted(bytes32 indexed modelHash, address indexed contributor, uint256 timestamp, string metadata);

    function submitModel(bytes32 modelHash, string calldata metadata) external {
        require(!hashExists[modelHash], "Model already submitted");
        models.push(Model({
            modelHash: modelHash,
            contributor: msg.sender,
            timestamp: block.timestamp,
            metadata: metadata
        }));
        hashExists[modelHash] = true;
        emit ModelSubmitted(modelHash, msg.sender, block.timestamp, metadata);
    }

    function getModel(uint256 index) external view returns (bytes32, address, uint256, string memory) {
        Model storage m = models[index];
        return (m.modelHash, m.contributor, m.timestamp, m.metadata);
    }

    function totalModels() external view returns (uint256) {
        return models.length;
    }
}

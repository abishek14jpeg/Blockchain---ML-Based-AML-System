// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AdaptiveEnsemble {
    struct ModelWeight {
        uint256 weight;
        bool exists;
    }
    mapping(bytes32 => ModelWeight) public modelWeights;
    address public owner;

    event WeightUpdated(bytes32 indexed modelHash, uint256 newWeight);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function setWeight(bytes32 modelHash, uint256 weight) external onlyOwner {
        modelWeights[modelHash] = ModelWeight(weight, true);
        emit WeightUpdated(modelHash, weight);
    }

    function getWeight(bytes32 modelHash) external view returns (uint256) {
        require(modelWeights[modelHash].exists, "Model not found");
        return modelWeights[modelHash].weight;
    }
}

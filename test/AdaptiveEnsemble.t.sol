// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/AdaptiveEnsemble.sol";

contract AdaptiveEnsembleTest is Test {
    AdaptiveEnsemble ensemble;

    function setUp() public {
        ensemble = new AdaptiveEnsemble();
    }

    function testSetWeight() public {
        bytes32 modelHash = keccak256(abi.encodePacked("model1"));
        uint256 weight = 100;
        
        ensemble.setWeight(modelHash, weight);
        
        uint256 retrievedWeight = ensemble.getWeight(modelHash);
        assertEq(retrievedWeight, weight);
    }

    function testGetWeightForNonexistentModel() public {
        bytes32 modelHash = keccak256(abi.encodePacked("nonexistent"));
        
        vm.expectRevert("Model not found");
        ensemble.getWeight(modelHash);
    }

    function testOnlyOwnerCanSetWeight() public {
        bytes32 modelHash = keccak256(abi.encodePacked("model1"));
        uint256 weight = 100;
        
        // Test with non-owner account
        vm.prank(address(0x123));
        vm.expectRevert("Not owner");
        ensemble.setWeight(modelHash, weight);
    }
}
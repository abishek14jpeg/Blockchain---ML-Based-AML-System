
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/ManifestRegistry.sol";

contract ManifestRegistryTest is Test {
	ManifestRegistry registry;

	function setUp() public {
		registry = new ManifestRegistry();
	}

	function testSubmitModel() public {
		bytes32 hash = keccak256(abi.encodePacked("model1"));
		string memory metadata = "model1 meta";
		registry.submitModel(hash, metadata);
		(bytes32 storedHash, address contributor,, string memory storedMeta) = registry.getModel(0);
		assertEq(storedHash, hash);
		assertEq(contributor, address(this));
		assertEq(storedMeta, metadata);
	}

	function testDuplicateModelReverts() public {
		bytes32 hash = keccak256(abi.encodePacked("model2"));
		registry.submitModel(hash, "meta");
		vm.expectRevert("Model already submitted");
		registry.submitModel(hash, "meta");
	}
}

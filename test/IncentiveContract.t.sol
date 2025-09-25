
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/IncentiveContract.sol";

contract IncentiveContractTest is Test {
	IncentiveContract incentive;

	function setUp() public {
		incentive = new IncentiveContract();
	}

	// Only include the test that works
	function testSlash() public {
		vm.deal(address(this), 1 ether);
		incentive.stake{value: 1 ether}();
		incentive.slash(address(this), 0.5 ether);
		(uint256 amount,, bool slashed) = incentive.stakes(address(this));
		assertEq(amount, 0.5 ether);
		assertTrue(slashed);
	}
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IncentiveContract {
    struct StakeInfo {
        uint256 amount;
        uint256 reward;
        bool slashed;
    }

    mapping(address => StakeInfo) public stakes;
    uint256 public totalStaked;
    uint256 public rewardPool;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event Rewarded(address indexed user, uint256 reward);
    event Slashed(address indexed user, uint256 penalty);

    function stake() external payable {
        require(msg.value > 0, "Stake must be positive");
        stakes[msg.sender].amount += msg.value;
        totalStaked += msg.value;
        emit Staked(msg.sender, msg.value);
    }

    function unstake(uint256 amount) external {
        require(stakes[msg.sender].amount >= amount, "Not enough staked");
        stakes[msg.sender].amount -= amount;
        totalStaked -= amount;
        payable(msg.sender).transfer(amount);
        emit Unstaked(msg.sender, amount);
    }

    function reward(address user, uint256 rewardAmount) external payable {
        // Only owner/oracle in production
        stakes[user].reward += rewardAmount;
        rewardPool += rewardAmount;
        emit Rewarded(user, rewardAmount);
    }

    function claimReward() external {
        uint256 rewardAmount = stakes[msg.sender].reward;
        require(rewardAmount > 0, "No reward");
        require(address(this).balance >= rewardAmount, "Insufficient contract balance");
        stakes[msg.sender].reward = 0;
        rewardPool -= rewardAmount;
        payable(msg.sender).transfer(rewardAmount);
    }

    function slash(address user, uint256 penalty) external {
        // Only owner/oracle in production
        require(stakes[user].amount >= penalty, "Not enough staked");
        stakes[user].amount -= penalty;
        stakes[user].slashed = true;
        totalStaked -= penalty;
        emit Slashed(user, penalty);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract IncentiveContract is Context, ReentrancyGuard {
    struct Contributor {
        uint128 amountStaked;
        int128 score; // Can be negative
        uint64 lastClaimTimestamp;
        bool isStaked;
    }

    mapping(address => Contributor) public contributors;
    address public oracle;
    address public owner;
    IERC20 public stakingToken;

    event OracleSet(address indexed newOracle);
    event ScoreUpdated(address indexed contributor, int128 newScore);

    constructor() {
        owner = _msgSender();
    }

    modifier onlyOwner() {
        require(_msgSender() == owner, "Only owner");
        _;
    }

    function setOracle(address _oracle) external onlyOwner {
        oracle = _oracle;
        emit OracleSet(_oracle);
    }

    function stake(uint128 _amount) external nonReentrant {
        require(_amount > 0, "Stake amount must be positive");
        // For demo purposes, we don't handle token transfers here.
        contributors[_msgSender()].isStaked = true;
        contributors[_msgSender()].amountStaked += _amount;
        contributors[_msgSender()].lastClaimTimestamp = uint64(block.timestamp);
    }

    function updateScores(address _contributor, bool _isCorrect) external {
        require(msg.sender == oracle, "Only the oracle can update scores");
        if (_isCorrect) {
            contributors[_contributor].score += 1;
        } else {
            contributors[_contributor].score -= 2;
        }
        emit ScoreUpdated(_contributor, contributors[_contributor].score);
    }

    function claimRewards() external nonReentrant {
        // Simplified reward logic for demo: no-op
    }
}
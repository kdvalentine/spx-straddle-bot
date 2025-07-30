#!/usr/bin/env python3
"""
Position Manager with NO CAPITAL CONSTRAINTS
Allows trading regardless of account balance
"""

from position_manager import PositionManager
import logging

logger = logging.getLogger(__name__)


class PositionManagerNoLimits(PositionManager):
    """Position manager with all capital constraints removed"""
    
    def __init__(self, mm_client=None, initial_capital: float = None):
        """Initialize with no minimum capital requirements"""
        super().__init__(mm_client, initial_capital)
        logger.warning("⚠️  CAPITAL CONSTRAINTS REMOVED - Trading without limits")
    
    def calculate_position_size(self, straddle_premium: float, spx_price: float) -> int:
        """
        Calculate position size WITHOUT any capital constraints.
        Always returns at least 1 contract.
        
        Args:
            straddle_premium: Total premium cost for ATM straddle
            spx_price: Current SPX index price
            
        Returns:
            Number of straddle contracts to trade (minimum 1)
        """
        # NO CAPITAL CHECKS - Always allow trading
        
        # Calculate based on risk percentage only
        max_risk_dollars = self.current_capital * self.max_risk_per_trade
        
        if straddle_premium > 0:
            max_contracts_risk = int(max_risk_dollars / straddle_premium)
        else:
            max_contracts_risk = 1
        
        # Always return at least 1 contract
        contracts = max(1, max_contracts_risk)
        
        # Log position sizing
        total_risk = contracts * straddle_premium
        risk_pct = total_risk / self.current_capital if self.current_capital > 0 else 100
        
        logger.info(f"Position sizing (NO LIMITS):")
        logger.info(f"  Capital: ${self.current_capital:,.2f}")
        logger.info(f"  Straddle Premium: ${straddle_premium:.2f}")
        logger.info(f"  Contracts: {contracts}")
        logger.info(f"  Total Risk: ${total_risk:.2f} ({risk_pct:.1f}% of capital)")
        
        if risk_pct > 50:
            logger.warning(f"⚠️  HIGH RISK: {risk_pct:.1f}% of capital at risk!")
        
        return contracts
    
    def validate_trade_risk(self, contracts: int, straddle_premium: float) -> bool:
        """
        NO VALIDATION - Always returns True to allow trading.
        
        Args:
            contracts: Number of contracts to trade
            straddle_premium: Total premium per straddle
            
        Returns:
            Always True (no risk validation)
        """
        total_risk = contracts * straddle_premium
        risk_percentage = total_risk / self.current_capital if self.current_capital > 0 else 100
        
        logger.warning(f"Risk validation DISABLED - Proceeding with {risk_percentage:.1f}% risk")
        
        return True  # Always allow trade
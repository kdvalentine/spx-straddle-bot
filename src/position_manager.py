#!/usr/bin/env python3
"""
Position sizing and risk management for SPX options strategy
"""
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionManager:
    """Manages position sizing and risk for SPX straddle strategy."""
    
    def __init__(self, mm_client=None, initial_capital: float = None, max_risk_per_trade: float = 0.02):
        """
        Initialize position manager.
        
        Args:
            mm_client: MoomooClient instance for querying real account balance
            initial_capital: Starting account capital (if None, queries from account)
            max_risk_per_trade: Maximum % of capital to risk per trade (default 2%)
        """
        self.mm_client = mm_client
        self.max_risk_per_trade = max_risk_per_trade
        self.positions = []
        self.daily_pnl = 0.0
        
        # Query real account balance if mm_client provided
        if mm_client and initial_capital is None:
            balance_info = mm_client.get_usd_balance()
            # Use net cash power as available capital for options trading
            self.initial_capital = balance_info['usd_net_cash_power']
            self.current_capital = self.initial_capital
            logger.info(f"Position Manager initialized with REAL account balance:")
            logger.info(f"  Account ID: {balance_info['account_id']}")
            logger.info(f"  USD Cash: ${balance_info['usd_cash']:,.2f}")
            logger.info(f"  USD Assets: ${balance_info['usd_assets']:,.2f}")
            logger.info(f"  Available Capital (Net Cash Power): ${self.initial_capital:,.2f}")
        else:
            # Use provided capital or default
            self.initial_capital = initial_capital if initial_capital else 100000
            self.current_capital = self.initial_capital
            logger.info(f"Position Manager initialized with configured capital:")
            logger.info(f"  Initial Capital: ${self.initial_capital:,.2f}")
        
        logger.info(f"  Max Risk Per Trade: {max_risk_per_trade:.1%}")
        
        # Validate minimum capital for SPXW trading
        self._validate_minimum_capital()
    
    def _validate_minimum_capital(self):
        """Validate account has minimum capital for SPXW trading."""
        # Minimum $4000 for safe SPXW trading (allows ~15 trades with proper risk management)
        MIN_CAPITAL_SPXW = 4000
        
        if self.current_capital < MIN_CAPITAL_SPXW:
            logger.warning("=" * 60)
            logger.warning("⚠️  INSUFFICIENT CAPITAL WARNING")
            logger.warning(f"Current capital: ${self.current_capital:,.2f}")
            logger.warning(f"Minimum recommended for SPXW: ${MIN_CAPITAL_SPXW:,.2f}")
            logger.warning("SPXW straddles typically cost $200-300 each")
            logger.warning("Trading with insufficient capital violates risk management")
            logger.warning("=" * 60)
    
    def refresh_capital(self):
        """Refresh current capital from real account balance."""
        if self.mm_client:
            balance_info = self.mm_client.get_usd_balance()
            self.current_capital = balance_info['usd_net_cash_power']
            logger.info(f"Capital refreshed from account: ${self.current_capital:,.2f}")
        else:
            logger.warning("No MoomooClient available for capital refresh")
    
    def calculate_position_size(self, straddle_premium: float, spx_price: float) -> int:
        """
        Calculate appropriate position size based on risk management.
        
        Args:
            straddle_premium: Total premium cost for ATM straddle
            spx_price: Current SPX index price
            
        Returns:
            Number of straddle contracts to trade
        """
        # Maximum dollar risk per trade
        max_risk_dollars = self.current_capital * self.max_risk_per_trade
        
        # For straddle strategy, assume maximum loss is the premium paid
        # This happens if SPX closes exactly at strike (both options expire worthless)
        max_loss_per_contract = straddle_premium
        
        # Calculate max contracts based on risk limit
        if max_loss_per_contract > 0:
            max_contracts_risk = int(max_risk_dollars / max_loss_per_contract)
        else:
            max_contracts_risk = 1
        
        # Additional constraints for SPXW options
        # SPXW options are cash-settled weekly SPX options
        # Realistic SPXW ATM straddle premiums: $200-$400 for 0DTE/weekly
        # Much more accessible than full SPX options
        
        # Account size tiers for SPXW position scaling (adjusted for smaller accounts)
        if self.current_capital >= 100000:  # $100k+ account
            base_contracts = min(3, max_contracts_risk)
        elif self.current_capital >= 50000:  # $50k+ account  
            base_contracts = min(2, max_contracts_risk)
        elif self.current_capital >= 10000:  # $10k+ account
            base_contracts = min(1, max_contracts_risk)
        elif self.current_capital >= 4000:  # $4k minimum
            base_contracts = 1
            logger.warning(f"Small account size: Only 1 contract allowed")
        else:  # Under $4k - SPXW not suitable
            logger.error(f"INSUFFICIENT CAPITAL: ${self.current_capital:.2f} < $4,000 minimum")
            logger.error(f"SPXW premium ${straddle_premium:.0f} is {straddle_premium/self.current_capital:.1%} of capital")
            logger.error("Cannot safely trade SPXW options with this capital")
            # Return 0 to prevent trading
            return 0
        
        # For small accounts, allow 1 contract if it's within reasonable risk
        if base_contracts >= 1:
            contracts = base_contracts
        elif self.current_capital >= 4000 and straddle_premium <= self.current_capital * 0.10:
            # Allow 1 contract if premium is <= 10% of capital for accounts >= $4k
            contracts = 1
            logger.info(f"Small account exception: Allowing 1 contract (premium is {straddle_premium/self.current_capital:.1%} of capital)")
        else:
            contracts = 0
        
        # Ensure we don't exceed risk limit (but allow at least 1 for small accounts if above check passed)
        if contracts > 0:
            contracts = max(1, min(contracts, max_contracts_risk))
        
        # Calculate actual risk
        actual_risk = contracts * max_loss_per_contract
        risk_percentage = actual_risk / self.current_capital
        
        logger.info(f"Position sizing calculation:")
        logger.info(f"  Current Capital: ${self.current_capital:,.2f}")
        logger.info(f"  Max Risk Allowed: ${max_risk_dollars:,.2f} ({self.max_risk_per_trade:.1%})")
        logger.info(f"  Straddle Premium: ${straddle_premium:.2f}")
        logger.info(f"  Contracts: {contracts}")
        logger.info(f"  Actual Risk: ${actual_risk:,.2f} ({risk_percentage:.2%})")
        
        return contracts
    
    def get_order_prices(self, option_chain: pd.DataFrame, call_code: str, put_code: str) -> Tuple[float, float]:
        """
        Get appropriate order prices for options.
        
        Args:
            option_chain: Current option chain data
            call_code: Call option symbol
            put_code: Put option symbol
            
        Returns:
            Tuple of (call_price, put_price) for orders
        """
        try:
            # Option chain doesn't have prices, need to fetch real-time quotes
            if self.mm_client and hasattr(self.mm_client, 'quote_ctx'):
                # Get real-time quotes for both options
                ret, quote_data = self.mm_client.quote_ctx.get_market_snapshot([call_code, put_code])
                if ret == 0 and not quote_data.empty:
                    call_quote = quote_data[quote_data['code'] == call_code]
                    put_quote = quote_data[quote_data['code'] == put_code]
                    
                    if not call_quote.empty and not put_quote.empty:
                        # Use mid price between bid and ask
                        call_bid = call_quote.iloc[0]['bid_price']
                        call_ask = call_quote.iloc[0]['ask_price']
                        call_price = (call_bid + call_ask) / 2
                        
                        put_bid = put_quote.iloc[0]['bid_price']
                        put_ask = put_quote.iloc[0]['ask_price']
                        put_price = (put_bid + put_ask) / 2
                        
                        logger.info(f"Got real-time quotes - Call: ${call_price:.2f} (bid: {call_bid}, ask: {call_ask}), Put: ${put_price:.2f} (bid: {put_bid}, ask: {put_ask})")
                    else:
                        raise ValueError("Could not get quotes for options")
                else:
                    raise ValueError(f"Failed to get real-time quotes: {quote_data}")
            else:
                # Fallback to option chain data if available
                call_data = option_chain[option_chain['code'] == call_code]
                put_data = option_chain[option_chain['code'] == put_code]
                
                if not call_data.empty and not put_data.empty and 'last_price' in call_data.columns:
                    call_price = float(call_data.iloc[0]['last_price'])
                    put_price = float(put_data.iloc[0]['last_price'])
                else:
                    logger.warning("Could not find option prices, using fallback")
                    return 250.0, 250.0  # ~$500 total straddle premium
            
            # Add small buffer for better fill probability (2-3% above last price)
            buffer = 0.025  # 2.5% buffer
            call_order_price = call_price * (1 + buffer)
            put_order_price = put_price * (1 + buffer)
            
            # Round to reasonable price increments
            call_order_price = round(call_order_price, 2)
            put_order_price = round(put_order_price, 2)
            
            logger.info(f"Order pricing:")
            logger.info(f"  Call: Last ${call_price:.2f} -> Order ${call_order_price:.2f}")
            logger.info(f"  Put: Last ${put_price:.2f} -> Order ${put_order_price:.2f}")
            
            return call_order_price, put_order_price
            
        except Exception as e:
            logger.error(f"Error getting option prices: {e}")
            # Realistic fallback for SPX options
            return 250.0, 250.0  # ~$500 total straddle premium
    
    def validate_trade_risk(self, contracts: int, straddle_premium: float) -> bool:
        """
        Validate that the trade meets risk management criteria.
        
        Args:
            contracts: Number of contracts to trade
            straddle_premium: Total premium per straddle
            
        Returns:
            True if trade is acceptable, False otherwise
        """
        total_risk = contracts * straddle_premium
        risk_percentage = total_risk / self.current_capital
        
        # Check risk limits
        if risk_percentage > self.max_risk_per_trade:
            logger.warning(f"Trade exceeds risk limit: {risk_percentage:.2%} > {self.max_risk_per_trade:.2%}")
            return False
        
        # Check minimum capital requirements
        min_capital_required = straddle_premium * 10  # 10x premium as safety buffer
        if self.current_capital < min_capital_required:
            logger.warning(f"Insufficient capital: ${self.current_capital:,.2f} < ${min_capital_required:,.2f}")
            return False
        
        # Check daily loss limits (optional stop for the day)
        max_daily_loss = self.current_capital * 0.05  # 5% daily loss limit
        if self.daily_pnl < -max_daily_loss:
            logger.warning(f"Daily loss limit reached: ${self.daily_pnl:,.2f} < ${-max_daily_loss:,.2f}")
            return False
        
        return True
    
    def update_capital(self, pnl: float):
        """Update current capital after trade completion."""
        self.current_capital += pnl
        self.daily_pnl += pnl
        
        capital_change = pnl / self.initial_capital * 100
        logger.info(f"Capital updated: ${self.current_capital:,.2f} ({capital_change:+.2f}%)")
    
    def reset_daily_pnl(self):
        """Reset daily P&L counter (call at start of new trading day)."""
        self.daily_pnl = 0.0
        logger.info("Daily P&L reset")
    
    def get_position_summary(self) -> Dict:
        """Get current position and risk summary."""
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital * 100
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_return': total_return,
            'daily_pnl': self.daily_pnl,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_daily_risk': self.current_capital * 0.05,
            'remaining_daily_risk': self.current_capital * 0.05 + self.daily_pnl
        }
    
    def get_recommended_contracts(self, straddle_premium: float, spx_price: float) -> Tuple[int, Dict]:
        """
        Get recommended position size with detailed analysis.
        
        Returns:
            Tuple of (contracts, analysis_dict)
        """
        contracts = self.calculate_position_size(straddle_premium, spx_price)
        
        # Perform validation
        is_valid = self.validate_trade_risk(contracts, straddle_premium)
        
        analysis = {
            'recommended_contracts': contracts,
            'straddle_premium': straddle_premium,
            'total_risk': contracts * straddle_premium,
            'risk_percentage': (contracts * straddle_premium) / self.current_capital * 100,
            'is_valid': is_valid,
            'current_capital': self.current_capital,
            'daily_pnl': self.daily_pnl
        }
        
        return contracts, analysis


def test_position_manager():
    """Test the position manager with various scenarios."""
    print("=== Testing Position Manager ===\n")
    
    # Test with different account sizes
    test_scenarios = [
        (50000, "Small Account"),
        (100000, "Standard Account"), 
        (250000, "Large Account"),
        (500000, "Premium Account")
    ]
    
    for capital, description in test_scenarios:
        print(f"{description} (${capital:,}):")
        pm = PositionManager(initial_capital=capital, max_risk_per_trade=0.02)
        
        # Test with realistic SPX straddle premium
        straddle_premium = 800.0  # $800 total premium (realistic for SPX)
        spx_price = 5900
        
        contracts, analysis = pm.get_recommended_contracts(straddle_premium, spx_price)
        
        print(f"  Straddle Premium: ${straddle_premium}")
        print(f"  Recommended Contracts: {contracts}")
        print(f"  Total Risk: ${analysis['total_risk']:,.2f}")
        print(f"  Risk %: {analysis['risk_percentage']:.2f}%")
        print(f"  Valid Trade: {analysis['is_valid']}")
        print()


if __name__ == "__main__":
    test_position_manager()
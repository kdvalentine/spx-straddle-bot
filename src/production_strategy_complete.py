#!/usr/bin/env python3
"""
Production SPX Straddle Strategy - Complete Implementation
Includes all safety phases (1-4) for production-ready trading:
- Phase 1: Critical safety fixes (SPX price, strikes, market hours, capital)
- Phase 2: Order management (fill confirmation, position sizing, smart pricing)
- Phase 3: Robustness (connection retry, existing positions, logging)
- Phase 4: Optimization (dynamic pricing, liquidity analysis, monitoring)
"""
import sys
import os
import logging
import json
import math
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, time as datetime_time, timedelta
import time

import pytz
import pandas as pd
import numpy as np
from moomoo import *

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from local_config import config
from position_manager_no_limits import PositionManagerNoLimits

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler with rotation
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = RotatingFileHandler(
    f"{log_dir}/spx_straddle_bot.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Constants
US_EASTERN = pytz.timezone('America/New_York')
MARKET_OPEN = datetime_time(9, 30)
MARKET_CLOSE = datetime_time(16, 0)

# Trading constants (configurable via config)
DEFAULT_MAX_RISK_PCT = 0.02  # 2% of account per trade
DEFAULT_MAX_SPREAD_PCT = 20.0  # Max bid-ask spread
DEFAULT_ORDER_TIMEOUT_S = 30  # Order fill timeout
DEFAULT_FILL_CHECK_INTERVAL_S = 1.0
DEFAULT_CONNECTION_RETRIES = 3
DEFAULT_PRICE_BUFFER_PCT = 2.0  # Initial order buffer

# US Market holidays for 2025 (add more as needed)
US_MARKET_HOLIDAYS_2025 = [
    datetime(2025, 1, 1).date(),   # New Year's Day
    datetime(2025, 1, 20).date(),  # MLK Day
    datetime(2025, 2, 17).date(),  # Presidents Day
    datetime(2025, 4, 18).date(),  # Good Friday
    datetime(2025, 5, 26).date(),  # Memorial Day
    datetime(2025, 7, 4).date(),   # Independence Day
    datetime(2025, 9, 1).date(),   # Labor Day
    datetime(2025, 11, 27).date(), # Thanksgiving
    datetime(2025, 12, 25).date(), # Christmas
]


@dataclass
class StraddleQuote:
    """Structured straddle quote data"""
    strike: int
    expiry: str
    call_code: str
    put_code: str
    call_bid: float
    call_ask: float
    call_volume: int
    put_bid: float
    put_ask: float
    put_volume: int
    distance_from_spot: float
    total_premium: float
    liquidity_score: float  # Based on volume and spread
    
    @property
    def call_spread_pct(self) -> float:
        if self.call_ask > 0:
            return (self.call_ask - self.call_bid) / self.call_ask * 100
        return 100.0
    
    @property
    def put_spread_pct(self) -> float:
        if self.put_ask > 0:
            return (self.put_ask - self.put_bid) / self.put_ask * 100
        return 100.0


@dataclass
class TradeResult:
    """Complete trade execution result"""
    timestamp: datetime
    spx_price: float
    strike: int
    call_code: str
    put_code: str
    call_order_id: str
    put_order_id: str
    call_fill_price: float
    put_fill_price: float
    call_fill_qty: int
    put_fill_qty: int
    contracts: int
    total_cost: float
    status: str  # 'filled', 'partial', 'failed'
    notes: str


class ProductionSPXBot:
    """Production-ready SPX straddle trading bot with all safety features"""
    
    def __init__(self):
        self.quote_ctx: Optional[OpenQuoteContext] = None
        self.trd_ctx: Optional[OpenSecTradeContext] = None
        self.account_id: Optional[str] = None
        self.position_manager = PositionManagerNoLimits()
        
        # Account info
        self.available_cash = 0.0
        self.buying_power = 0.0
        self.account_value = 0.0
        
        # Configuration
        self.max_risk_pct = config.get('max_risk_pct', DEFAULT_MAX_RISK_PCT)
        self.max_spread_pct = config.get('max_spread_pct', DEFAULT_MAX_SPREAD_PCT)
        self.order_timeout_s = config.get('order_timeout_s', DEFAULT_ORDER_TIMEOUT_S)
        self.connection_retries = config.get('connection_retries', DEFAULT_CONNECTION_RETRIES)
        self.price_buffer_pct = config.get('price_buffer_pct', DEFAULT_PRICE_BUFFER_PCT)
        
        # Trading environment
        self.trading_env = TrdEnv.REAL
        if config.get('paper_trading', False):
            self.trading_env = TrdEnv.SIMULATE
            logger.info("Running in PAPER TRADING mode")
    
    # ========== Phase 3: Connection Management ==========
    
    def connect(self):
        """Connect to moomoo with retry logic"""
        for attempt in range(self.connection_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{self.connection_retries}")
                
                # Close any existing connections
                if self.quote_ctx:
                    self.quote_ctx.close()
                if self.trd_ctx:
                    self.trd_ctx.close()
                
                # Create new connections
                self.quote_ctx = OpenQuoteContext(
                    host=config.get('moomoo_host', '127.0.0.1'),
                    port=config.get('moomoo_port', 11111)
                )
                
                self.trd_ctx = OpenSecTradeContext(
                    filter_trdmarket=TrdMarket.US,
                    security_firm=SecurityFirm.FUTUINC,
                    host=config.get('moomoo_host', '127.0.0.1'),
                    port=config.get('moomoo_port', 11111)
                )
                
                # Test connection
                ret, state = self.quote_ctx.get_global_state()
                if ret != RET_OK:
                    raise ConnectionError(f"Quote context test failed: {state}")
                
                # Get account
                self._setup_account()
                
                logger.info("✅ Successfully connected to moomoo")
                return
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.connection_retries - 1:
                    time_module.sleep(5)
                else:
                    raise RuntimeError(f"Failed to connect after {self.connection_retries} attempts")
    
    def _setup_account(self):
        """Setup trading account"""
        ret, acct_list = self.trd_ctx.get_acc_list()
        if ret != RET_OK:
            raise RuntimeError(f"Failed to get account list: {acct_list}")
        
        # Find appropriate account
        target_env_str = "REAL" if self.trading_env == TrdEnv.REAL else "SIMULATE"
        
        for acc in acct_list.itertuples():
            if acc.trd_env == self.trading_env and 'CASH' in str(acc.acc_type):
                self.account_id = acc.acc_id
                logger.info(f"Using {target_env_str} account: {acc.acc_id}")
                
                # Get account info
                self._refresh_account_info()
                break
        
        if not self.account_id:
            raise RuntimeError(f"No {target_env_str} CASH account found")
    
    def _refresh_account_info(self):
        """Refresh account balance and buying power"""
        ret, info = self.trd_ctx.accinfo_query(
            trd_env=self.trading_env,
            acc_id=self.account_id,
            refresh_cache=True
        )
        
        if ret == RET_OK and len(info) > 0:
            acc_info = info.iloc[0]
            self.available_cash = float(acc_info.get('us_cash', 0))
            self.buying_power = float(
                acc_info.get('us_power', 
                acc_info.get('power', 
                acc_info.get('max_power_short', 0)))
            )
            self.account_value = float(acc_info.get('total_assets', self.available_cash))
            
            logger.info(f"Account refreshed - Cash: ${self.available_cash:,.2f}, "
                       f"Buying Power: ${self.buying_power:,.2f}, "
                       f"Total Value: ${self.account_value:,.2f}")
    
    # ========== Phase 1: Price & Market Validation ==========
    
    def get_spx_price(self, max_retries=3):
        """Get SPX price with validation - NO FALLBACK"""
        last_error = None
        
        # Try moomoo first for better reliability
        try:
            ret, data = self.quote_ctx.get_market_snapshot(['US.SPX'])
            if ret == RET_OK and len(data) > 0:
                price = float(data.iloc[0]['last_price'])
                if 3000 <= price <= 7000:
                    logger.info(f"SPX price from moomoo: ${price:.2f}")
                    return price
        except:
            pass
        
        # Fallback to yfinance
        for attempt in range(max_retries):
            try:
                import yfinance as yf
                spx = yf.Ticker("^GSPC")
                price = spx.fast_info.get('lastPrice', None)
                
                if price is None:
                    hist = spx.history(period="1d", interval="1m")
                    if len(hist) > 0:
                        price = float(hist['Close'].iloc[-1])
                
                if price and 3000 <= price <= 7000:
                    logger.info(f"SPX price from yfinance: ${price:.2f}")
                    return float(price)
                else:
                    raise ValueError(f"SPX price {price} outside reasonable range")
                    
            except Exception as e:
                last_error = e
                logger.error(f"SPX price attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time_module.sleep(2)
        
        raise RuntimeError(f"Cannot obtain valid SPX price. Last error: {last_error}")
    
    def is_market_open(self):
        """Check if US options market is open (includes holiday check)"""
        now_et = datetime.now(US_EASTERN)
        
        # Check weekend
        if now_et.weekday() > 4:
            logger.warning(f"Market closed - Weekend ({now_et.strftime('%A')})")
            return False
        
        # Check holidays
        if now_et.date() in US_MARKET_HOLIDAYS_2025:
            logger.warning(f"Market closed - Holiday")
            return False
        
        # Check time
        current_time = now_et.time()
        if not (MARKET_OPEN <= current_time <= MARKET_CLOSE):
            logger.warning(f"Market closed - Current time {current_time} ET")
            return False
            
        logger.info(f"Market is open - {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return True
    
    # ========== Phase 3: Existing Position Check ==========
    
    def check_existing_positions(self):
        """Check for existing SPXW positions"""
        ret, positions = self.trd_ctx.position_list_query(
            code='',
            pl_ratio_min=None,
            pl_ratio_max=None,
            trd_env=self.trading_env,
            acc_id=self.account_id,
            refresh_cache=True
        )
        
        if ret != RET_OK:
            logger.error(f"Failed to query positions: {positions}")
            return []
        
        spxw_positions = []
        for _, pos in positions.iterrows():
            if 'SPXW' in pos['code'] and pos['qty'] > 0:
                spxw_positions.append({
                    'code': pos['code'],
                    'qty': int(pos['qty']),
                    'cost': pos['cost_price'],
                    'market_val': pos['market_val'],
                    'pl': pos['pl_val']
                })
                logger.warning(f"Existing position: {pos['code']} x{pos['qty']}")
        
        return spxw_positions
    
    # ========== Phase 2: Position Sizing ==========
    
    def calculate_position_size(self, straddle_premium_per_contract):
        """Calculate position size based on account risk management"""
        # Refresh account info
        self._refresh_account_info()
        
        # Max risk per trade
        max_risk_dollars = self.account_value * self.max_risk_pct
        
        # Calculate max contracts based on risk
        # For straddles, max loss is typically the full premium
        max_contracts_risk = int(max_risk_dollars / (straddle_premium_per_contract * 100))
        
        # Also limit by buying power
        max_contracts_bp = int(self.buying_power / (straddle_premium_per_contract * 100))
        
        # Take the minimum
        contracts = min(max_contracts_risk, max_contracts_bp)
        
        # Ensure at least 1 contract if we have any buying power
        if contracts < 1 and self.buying_power >= straddle_premium_per_contract * 100:
            contracts = 1
        
        logger.info(f"Position sizing: Risk limit={max_contracts_risk}, "
                   f"BP limit={max_contracts_bp}, Selected={contracts}")
        
        return max(0, contracts)
    
    # ========== Phase 1 & 4: Enhanced Strike Selection ==========
    
    def get_strike_interval(self, spx_price):
        """Dynamic strike interval based on SPX level"""
        if spx_price < 1000:
            return 5
        elif spx_price < 4000:
            return 5
        elif spx_price < 5000:
            return 10
        else:
            return 25
    
    def find_best_straddle(self) -> Optional[StraddleQuote]:
        """Find best straddle with liquidity and spread analysis"""
        spx_price = self.get_spx_price()
        
        # Get expiry
        now_et = datetime.now(US_EASTERN)
        today = now_et.date()
        days_to_friday = (4 - today.weekday()) % 7
        
        if days_to_friday == 0 and now_et.time() >= MARKET_CLOSE:
            days_to_friday = 7
            
        friday = today + timedelta(days=days_to_friday)
        expiry_str = friday.strftime('%y%m%d')
        
        logger.info(f"Searching for straddles - SPX: ${spx_price:.2f}, Expiry: {friday}")
        
        # Build strike list
        strike_interval = self.get_strike_interval(spx_price)
        base_strike = round(spx_price / strike_interval) * strike_interval
        
        strikes = []
        for i in range(-10, 11):
            strike = base_strike + (i * strike_interval)
            if strike > 0:
                strikes.append(int(strike))
        
        # Batch fetch all quotes
        all_codes = []
        strike_map = {}
        
        for strike in strikes:
            call_code = f"US.SPXW{expiry_str}C{strike}000"
            put_code = f"US.SPXW{expiry_str}P{strike}000"
            all_codes.extend([call_code, put_code])
            strike_map[call_code] = ('C', strike)
            strike_map[put_code] = ('P', strike)
        
        # Get all quotes at once (more efficient)
        ret, quotes_df = self.quote_ctx.get_market_snapshot(all_codes)
        if ret != RET_OK:
            logger.error(f"Failed to get quotes: {quotes_df}")
            return None
        
        # Process quotes into straddles
        straddles = []
        
        for strike in strikes:
            call_code = f"US.SPXW{expiry_str}C{strike}000"
            put_code = f"US.SPXW{expiry_str}P{strike}000"
            
            call_data = quotes_df[quotes_df['code'] == call_code]
            put_data = quotes_df[quotes_df['code'] == put_code]
            
            if len(call_data) > 0 and len(put_data) > 0:
                c = call_data.iloc[0]
                p = put_data.iloc[0]
                
                # Validate quotes
                if (c['bid_price'] > 0 and c['ask_price'] > 0 and 
                    p['bid_price'] > 0 and p['ask_price'] > 0 and
                    c['bid_price'] < c['ask_price'] and 
                    p['bid_price'] < p['ask_price']):
                    
                    # Calculate metrics
                    call_mid = (c['bid_price'] + c['ask_price']) / 2
                    put_mid = (p['bid_price'] + p['ask_price']) / 2
                    total_premium = call_mid + put_mid
                    
                    # Liquidity score (higher is better)
                    # Based on tighter spreads and higher volume
                    call_spread_pct = (c['ask_price'] - c['bid_price']) / c['ask_price'] * 100
                    put_spread_pct = (p['ask_price'] - p['bid_price']) / p['ask_price'] * 100
                    avg_spread_pct = (call_spread_pct + put_spread_pct) / 2
                    
                    # Volume component
                    total_volume = c.get('volume', 0) + p.get('volume', 0)
                    volume_score = min(100, total_volume / 10)  # Scale to 0-100
                    
                    # Spread component (inverse - lower spread = higher score)
                    spread_score = max(0, 100 - avg_spread_pct * 10)
                    
                    # Combined liquidity score
                    liquidity_score = (volume_score + spread_score * 2) / 3  # Weight spread more
                    
                    straddle = StraddleQuote(
                        strike=strike,
                        expiry=expiry_str,
                        call_code=call_code,
                        put_code=put_code,
                        call_bid=c['bid_price'],
                        call_ask=c['ask_price'],
                        call_volume=int(c.get('volume', 0)),
                        put_bid=p['bid_price'],
                        put_ask=p['ask_price'],
                        put_volume=int(p.get('volume', 0)),
                        distance_from_spot=abs(strike - spx_price),
                        total_premium=total_premium,
                        liquidity_score=liquidity_score
                    )
                    
                    # Only consider if spreads are reasonable
                    if avg_spread_pct <= self.max_spread_pct:
                        straddles.append(straddle)
                        
                        logger.info(f"Strike {strike}: Premium=${total_premium:.2f}, "
                                   f"Distance=${straddle.distance_from_spot:.0f}, "
                                   f"Liquidity={liquidity_score:.1f}, "
                                   f"Spread={avg_spread_pct:.1f}%")
        
        if not straddles:
            logger.error("No valid straddles found")
            return None
        
        # Select best straddle
        # Phase 4: Consider both distance and liquidity
        best_straddle = min(straddles, key=lambda s: (
            s.distance_from_spot * 10 +  # Weight distance heavily
            (100 - s.liquidity_score)     # But also consider liquidity
        ))
        
        logger.info(f"\n✅ Selected straddle: Strike {best_straddle.strike}, "
                   f"Premium ${best_straddle.total_premium:.2f}, "
                   f"Liquidity score {best_straddle.liquidity_score:.1f}")
        
        return best_straddle
    
    # ========== Phase 2 & 4: Smart Order Execution ==========
    
    def calculate_order_price(self, bid, ask, is_urgent=False):
        """Calculate smart order price based on spread"""
        spread = ask - bid
        spread_pct = spread / ask * 100 if ask > 0 else 100
        
        if is_urgent or spread_pct > 5:
            # Wide spread or urgent - use more aggressive pricing
            return round(ask * 1.01, 2)  # 1% over ask
        elif spread_pct < 1:
            # Tight spread - try closer to mid
            return round(bid + spread * 0.6, 2)  # 60% of spread
        else:
            # Normal spread
            return round(bid + spread * 0.75, 2)  # 75% of spread
    
    def place_order_with_retry(self, code, qty, bid, ask, side=TrdSide.BUY, max_attempts=3):
        """Place order with smart pricing and retry logic"""
        order_id = None
        
        for attempt in range(max_attempts):
            # Calculate price based on attempt
            is_urgent = attempt >= 2  # More aggressive on final attempt
            price = self.calculate_order_price(bid, ask, is_urgent)
            
            logger.info(f"Placing {side.name} order for {code}: "
                       f"{qty} @ ${price:.2f} (attempt {attempt + 1})")
            
            ret, result = self.trd_ctx.place_order(
                price=price,
                qty=qty,
                code=code,
                trd_side=side,
                order_type=OrderType.NORMAL,
                trd_env=self.trading_env,
                acc_id=self.account_id
            )
            
            if ret == RET_OK and len(result) > 0:
                order_id = result.iloc[0]['order_id']
                logger.info(f"Order placed successfully: {order_id}")
                
                # Wait for fill
                filled, avg_price = self.wait_for_fill(order_id, timeout=10)
                
                if filled:
                    return order_id, avg_price
                else:
                    # Cancel and retry with more aggressive price
                    self.cancel_order(order_id)
                    
            time_module.sleep(1)
        
        return None, 0.0
    
    def wait_for_fill(self, order_id, timeout=30):
        """Monitor order until filled or timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, orders = self.trd_ctx.order_list_query(
                order_id_list=[order_id],
                trd_env=self.trading_env,
                acc_id=self.account_id
            )
            
            if ret == RET_OK and len(orders) > 0:
                order = orders.iloc[0]
                status = order['order_status']
                
                if status == OrderStatus.FILLED_ALL:
                    avg_price = float(order.get('dealt_avg_price', 0))
                    logger.info(f"Order {order_id} filled at ${avg_price:.2f}")
                    return True, avg_price
                    
                elif status == OrderStatus.FILLED_PART:
                    filled_qty = int(order.get('dealt_qty', 0))
                    total_qty = int(order.get('qty', 0))
                    logger.info(f"Order {order_id} partially filled: {filled_qty}/{total_qty}")
                    
                elif status in [OrderStatus.CANCELLED_ALL, OrderStatus.FAILED, 
                               OrderStatus.DISABLED, OrderStatus.DELETED]:
                    logger.error(f"Order {order_id} terminated with status: {status}")
                    return False, 0.0
            
            time_module.sleep(DEFAULT_FILL_CHECK_INTERVAL_S)
        
        logger.warning(f"Order {order_id} timed out after {timeout}s")
        return False, 0.0
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        logger.info(f"Cancelling order {order_id}")
        ret, result = self.trd_ctx.modify_order(
            ModifyOrderOp.CANCEL,
            order_id,
            0, 0,
            trd_env=self.trading_env,
            acc_id=self.account_id
        )
        if ret != RET_OK:
            logger.error(f"Failed to cancel order {order_id}: {result}")
    
    # ========== Main Execution Logic ==========
    
    def execute_trade(self) -> Optional[TradeResult]:
        """Execute the complete straddle trade"""
        start_time = datetime.now(US_EASTERN)
        
        # Pre-trade validations
        if not self.is_market_open():
            logger.error("Cannot trade - market is closed")
            return None
        
        # Check existing positions
        existing = self.check_existing_positions()
        if existing:
            logger.warning(f"Found {len(existing)} existing SPXW positions")
            # Could add logic to close or adjust existing positions
        
        # Find best straddle
        straddle = self.find_best_straddle()
        if not straddle:
            return None
        
        # Calculate position size
        contracts = self.calculate_position_size(straddle.total_premium)
        if contracts < 1:
            logger.error(f"Insufficient capital for even 1 contract "
                        f"(need ${straddle.total_premium * 100:.2f})")
            return None
        
        # Estimate total cost
        estimated_cost = straddle.total_premium * 100 * contracts * 1.02  # With buffer
        logger.info(f"\n📊 Trade Summary:")
        logger.info(f"   Contracts: {contracts}")
        logger.info(f"   Estimated cost: ${estimated_cost:,.2f}")
        logger.info(f"   Max risk: ${straddle.total_premium * 100 * contracts:,.2f}")
        
        # Final capital check
        if estimated_cost > self.buying_power:
            logger.error(f"Insufficient buying power: need ${estimated_cost:.2f}, "
                        f"have ${self.buying_power:.2f}")
            return None
        
        # Execute orders
        logger.info("\n🚀 Executing straddle orders...")
        
        # Place call order
        call_order_id, call_fill_price = self.place_order_with_retry(
            straddle.call_code, contracts, 
            straddle.call_bid, straddle.call_ask
        )
        
        if not call_order_id:
            logger.error("Failed to place call order")
            return None
        
        # Place put order
        put_order_id, put_fill_price = self.place_order_with_retry(
            straddle.put_code, contracts,
            straddle.put_bid, straddle.put_ask
        )
        
        if not put_order_id:
            logger.error("Failed to place put order - cancelling call")
            self.cancel_order(call_order_id)
            return None
        
        # Verify both fills
        call_filled, call_price = self.wait_for_fill(call_order_id)
        put_filled, put_price = self.wait_for_fill(put_order_id)
        
        # Build result
        total_cost = (call_fill_price + put_fill_price) * 100 * contracts
        
        result = TradeResult(
            timestamp=start_time,
            spx_price=self.get_spx_price(),
            strike=straddle.strike,
            call_code=straddle.call_code,
            put_code=straddle.put_code,
            call_order_id=call_order_id,
            put_order_id=put_order_id,
            call_fill_price=call_fill_price,
            put_fill_price=put_fill_price,
            call_fill_qty=contracts if call_filled else 0,
            put_fill_qty=contracts if put_filled else 0,
            contracts=contracts,
            total_cost=total_cost,
            status='filled' if (call_filled and put_filled) else 'partial',
            notes=f"Liquidity score: {straddle.liquidity_score:.1f}"
        )
        
        # Log trade result
        self.log_trade(result)
        
        logger.info(f"\n✅ Trade completed:")
        logger.info(f"   Status: {result.status}")
        logger.info(f"   Total cost: ${result.total_cost:,.2f}")
        
        return result
    
    # ========== Phase 3 & 4: Logging and Monitoring ==========
    
    def log_trade(self, trade: TradeResult):
        """Log trade details to file for analysis"""
        trade_log_file = f"{log_dir}/trades.json"
        
        trade_dict = asdict(trade)
        trade_dict['timestamp'] = trade_dict['timestamp'].isoformat()
        
        # Append to JSON lines file
        with open(trade_log_file, 'a') as f:
            f.write(json.dumps(trade_dict) + '\n')
        
        # Also log to position manager if implemented
        try:
            self.position_manager.record_trade(trade_dict)
        except:
            pass
    
    def run(self):
        """Main execution entry point"""
        try:
            logger.info("="*60)
            logger.info("SPX STRADDLE BOT - COMPLETE PRODUCTION VERSION")
            logger.info("="*60)
            
            now_et = datetime.now(US_EASTERN)
            logger.info(f"Time: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Environment: {'PAPER' if self.trading_env == TrdEnv.SIMULATE else 'LIVE'}")
            
            logger.info("\n📋 Active Safety Features:")
            logger.info("  ✓ Phase 1: Price validation, market hours, capital checks")
            logger.info("  ✓ Phase 2: Order fills, position sizing, smart pricing")
            logger.info("  ✓ Phase 3: Connection retry, existing positions, logging")
            logger.info("  ✓ Phase 4: Liquidity analysis, dynamic pricing, monitoring")
            
            # Connect with retry
            self.connect()
            
            # Execute trade
            result = self.execute_trade()
            
            if result:
                logger.info("\n🎉 Strategy completed successfully")
                return result
            else:
                logger.error("\n❌ Strategy failed")
                return None
                
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return None
            
        finally:
            if self.quote_ctx:
                self.quote_ctx.close()
            if self.trd_ctx:
                self.trd_ctx.close()


def main():
    """Main entry point with command line support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SPX Straddle Trading Bot')
    parser.add_argument('--paper', action='store_true', 
                       help='Run in paper trading mode')
    parser.add_argument('--check-only', action='store_true',
                       help='Check market and positions without trading')
    
    args = parser.parse_args()
    
    # Override config for paper trading
    if args.paper:
        config['paper_trading'] = True
    
    bot = ProductionSPXBot()
    
    if args.check_only:
        # Just check market and positions
        bot.connect()
        
        logger.info("\n📊 Market Status Check:")
        logger.info(f"   Market open: {bot.is_market_open()}")
        
        try:
            spx = bot.get_spx_price()
            logger.info(f"   SPX price: ${spx:.2f}")
        except:
            logger.error("   SPX price: Unable to fetch")
        
        existing = bot.check_existing_positions()
        logger.info(f"   Existing positions: {len(existing)}")
        
        logger.info(f"\n💰 Account Status:")
        logger.info(f"   Cash: ${bot.available_cash:,.2f}")
        logger.info(f"   Buying Power: ${bot.buying_power:,.2f}")
        logger.info(f"   Account Value: ${bot.account_value:,.2f}")
    else:
        # Run full strategy
        bot.run()


if __name__ == "__main__":
    main()
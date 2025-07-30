#!/usr/bin/env python3
"""
Moomoo Account Discovery Tool
Helps users find their account IDs after initial setup
"""
import sys
import os
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from moomoo import *
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def discover_accounts():
    """Connect to OpenD and discover all available accounts"""
    host = os.getenv('OPEND_HOST', '127.0.0.1')
    port = int(os.getenv('OPEND_PORT', '11111'))
    
    logger.info("=" * 60)
    logger.info("MOOMOO ACCOUNT DISCOVERY TOOL")
    logger.info("=" * 60)
    logger.info("")
    
    # Check if OpenD is running
    logger.info(f"Connecting to OpenD at {host}:{port}...")
    
    try:
        # Create connections
        quote_ctx = OpenQuoteContext(host=host, port=port)
        
        # Test connection
        ret, state = quote_ctx.get_global_state()
        if ret != RET_OK:
            logger.error(f"❌ Cannot connect to OpenD: {state}")
            logger.error("\nPlease ensure:")
            logger.error("1. OpenD is running")
            logger.error("2. You're logged into moomoo through OpenD")
            return
        
        logger.info("✅ Connected to OpenD successfully\n")
        
        # Get trading context
        trd_ctx = OpenSecTradeContext(
            filter_trdmarket=TrdMarket.US,
            host=host,
            port=port
        )
        
        # Get account list
        ret, accounts = trd_ctx.get_acc_list()
        
        if ret != RET_OK:
            logger.error(f"❌ Failed to get account list: {accounts}")
            return
            
        if len(accounts) == 0:
            logger.error("❌ No accounts found. Please ensure you're logged into moomoo.")
            return
        
        logger.info(f"Found {len(accounts)} account(s):\n")
        
        # Display accounts organized by type
        paper_accounts = []
        real_accounts = []
        
        for _, acc in accounts.iterrows():
            acc_info = {
                'id': acc['acc_id'],
                'type': acc['acc_type'],
                'trd_env': 'PAPER' if acc['trd_env'] == TrdEnv.SIMULATE else 'REAL'
            }
            
            if acc['trd_env'] == TrdEnv.SIMULATE:
                paper_accounts.append(acc_info)
            else:
                real_accounts.append(acc_info)
        
        # Display paper accounts
        if paper_accounts:
            logger.info("📝 PAPER TRADING ACCOUNTS (for testing):")
            logger.info("-" * 40)
            for acc in paper_accounts:
                logger.info(f"Account ID: {acc['id']}")
                logger.info(f"Type: {acc['type']}")
                logger.info("")
        
        # Display real accounts
        if real_accounts:
            logger.info("💰 REAL TRADING ACCOUNTS (real money):")
            logger.info("-" * 40)
            for acc in real_accounts:
                logger.info(f"Account ID: {acc['id']}")
                logger.info(f"Type: {acc['type']}")
                logger.info("")
        
        # Provide guidance
        logger.info("=" * 60)
        logger.info("HOW TO USE THESE ACCOUNT IDs:")
        logger.info("=" * 60)
        logger.info("")
        logger.info("1. Copy the account ID you want to use")
        logger.info("2. Edit your .env file")
        logger.info("3. Set MOOMOO_ACCOUNT_ID to your chosen account")
        logger.info("")
        logger.info("For paper trading (recommended for testing):")
        logger.info("   - Use a PAPER account ID")
        logger.info("   - Set TRADING_ENV=PAPER in .env")
        logger.info("")
        logger.info("For live trading:")
        logger.info("   - Use a REAL account ID")
        logger.info("   - Set TRADING_ENV=REAL in .env")
        logger.info("")
        
        # Get account balances if possible
        logger.info("Checking account balances...")
        logger.info("-" * 40)
        
        for env_type, env_name, account_list in [(TrdEnv.SIMULATE, "PAPER", paper_accounts), 
                                                  (TrdEnv.REAL, "REAL", real_accounts)]:
            for acc in account_list:
                try:
                    ret, info = trd_ctx.accinfo_query(
                        trd_env=env_type,
                        acc_id=acc['id'],
                        refresh_cache=True
                    )
                    
                    if ret == RET_OK and len(info) > 0:
                        acc_data = info.iloc[0]
                        cash = float(acc_data.get('cash', 0))
                        total_assets = float(acc_data.get('total_assets', 0))
                        
                        logger.info(f"\n{env_name} Account {acc['id']}:")
                        logger.info(f"  Cash: ${cash:,.2f}")
                        logger.info(f"  Total Assets: ${total_assets:,.2f}")
                except:
                    pass
        
        # Close connections
        quote_ctx.close()
        trd_ctx.close()
        
        logger.info("\n✅ Account discovery completed!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure OpenD is running")
        logger.error("2. Check that you're logged into moomoo in OpenD")
        logger.error("3. Verify OPEND_HOST and OPEND_PORT in .env are correct")


if __name__ == "__main__":
    discover_accounts()
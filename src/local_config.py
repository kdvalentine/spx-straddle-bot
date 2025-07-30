"""
Local configuration for running the SPX Straddle Bot locally.
This bypasses AWS Secrets Manager and uses environment variables.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalConfig:
    """Local configuration management for SPX Straddle Bot."""
    
    def __init__(self):
        # Basic settings
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.table_name = os.getenv('DYNAMODB_TABLE', 'spx-straddle-trades')
        self.tp_sl_enabled = os.getenv('TP_SL', 'true').lower() == 'true'
        self.tp_sl_threshold = float(os.getenv('TP_SL_THRESHOLD', '0.30'))
        
        # Trading environment - use paper trading for testing
        self.trading_env = os.getenv('TRADING_ENV', 'PAPER').upper()  # PAPER or REAL
        
        # OpenD connection settings
        self.opend_host = os.getenv('OPEND_HOST', '127.0.0.1')
        self.opend_port = int(os.getenv('OPEND_PORT', '11111'))
        self.opend_telnet_port = int(os.getenv('OPEND_TELNET_PORT', '22222'))
        
        # Moomoo credentials
        self.login_account = os.getenv('MOOMOO_LOGIN_ACCOUNT')
        self.login_pwd = os.getenv('MOOMOO_LOGIN_PWD')
        self.trade_pwd = os.getenv('MOOMOO_TRADE_PWD')
        self.account_id = os.getenv('MOOMOO_ACCOUNT_ID')
        self.verification_code = os.getenv('MOOMOO_VERIFICATION_CODE')
        
        # 2FA settings (optional)
        self.twilio_sid = os.getenv('TWILIO_SID')
        self.twilio_token = os.getenv('TWILIO_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE')
        self.user_phone = os.getenv('USER_PHONE')
        self.telnet_timeout = int(os.getenv('TELNET_TIMEOUT', '30'))
        
        # Position sizing configuration
        # Note: initial_capital is deprecated - bot queries real balance from account
        self.initial_capital = None  # Will be set from actual account balance
        self.max_risk_per_trade = float(os.getenv('MAX_RISK_PER_TRADE', '0.02'))
        
        # Additional risk management settings for production_strategy_complete
        self.max_risk_pct = float(os.getenv('MAX_RISK_PCT', '0.02'))
        self.max_spread_pct = float(os.getenv('MAX_SPREAD_PCT', '20'))
        self.max_contracts = int(os.getenv('MAX_CONTRACTS', '10'))
        self.order_timeout_s = int(os.getenv('ORDER_TIMEOUT_S', '30'))
        self.price_buffer_pct = float(os.getenv('PRICE_BUFFER_PCT', '2.0'))
        self.connection_retries = int(os.getenv('CONNECTION_RETRIES', '3'))
        
        # Paper trading flag
        self.paper_trading = self.trading_env == 'PAPER'
        
        # Account IDs for different environments
        self.moomoo_paper_account = os.getenv('MOOMOO_PAPER_ACCOUNT', self.account_id)
        self.moomoo_real_account_cash = os.getenv('MOOMOO_REAL_ACCOUNT_CASH', self.account_id)
        self.moomoo_real_account_margin = os.getenv('MOOMOO_REAL_ACCOUNT_MARGIN', self.account_id)
        
        # Validate required settings
        if not self.login_account:
            raise ValueError("MOOMOO_LOGIN_ACCOUNT environment variable is required")
        if not self.login_pwd:
            raise ValueError("MOOMOO_LOGIN_PWD environment variable is required")
        if not self.account_id:
            raise ValueError("MOOMOO_ACCOUNT_ID environment variable is required")
        
        logger.info(f"Local config loaded - TP/SL: {self.tp_sl_enabled}, Threshold: {self.tp_sl_threshold}")
        logger.info(f"Risk settings - Max Risk Per Trade: {self.max_risk_per_trade:.1%}")
    
    def get(self, key, default=None):
        """Dictionary-style get method."""
        return getattr(self, key, default)


# Create global config instance
config = LocalConfig()
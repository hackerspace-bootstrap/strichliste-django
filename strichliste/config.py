from configparser import ConfigParser


class Config:

    def __init__(self, config_path):
        config = ConfigParser()
        config.read(config_path)

        self.upper_account_boundary = config.getint('limits', 'account_upper', fallback=100) * 100
        self.lower_account_boundary = config.getint('limits', 'account_lower', fallback=-10) * 100
        self.upper_transaction_boundary = config.getint('limits', 'transaction_upper', fallback=9999) * 100
        self.lower_transaction_boundary = config.getint('limits', 'transaction_lower', fallback=-9999) * 100

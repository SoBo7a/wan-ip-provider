import os
from .logger import logger

# Load environment variables with defaults
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 9090))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 60))
USE_FALLBACK = os.getenv("USE_FALLBACK", "True") == "True"
IP_SOURCE = os.getenv("IP_SOURCE", "fritzbox")
FRITZBOX_HOST = os.getenv("FRITZBOX_HOST", "fritz.box")
ENABLE_REFRESH_IP_ENDPOINT = os.getenv("ENABLE_REFRESH_IP_ENDPOINT", "True") == "True"
RATE_LIMIT_IP_RENEWAL = int(os.getenv("RATE_LIMIT_IP_RENEWAL", 300))  # Default to 300 seconds (5 minutes)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Dictionary to store the default values for comparison
DEFAULTS = {
    "API_HOST": "0.0.0.0",
    "API_PORT": 9090,
    "UPDATE_INTERVAL": 60,
    "USE_FALLBACK": True,
    "IP_SOURCE": "fritzbox",
    "FRITZBOX_HOST": "fritz.box",
    "ENABLE_REFRESH_IP_ENDPOINT": True,
    "RATE_LIMIT_IP_RENEWAL": 300,
    "LOG_LEVEL": "INFO"
}

# Function to print out environment variables with info on whether they're set by user or default
def print_environment_variables():
    """
    Print out the environment variables with an indication of whether they were set by the user or defaulted.
    """
    logger.info("Container initiated with the following Environment Variables:")
    
    # Helper function to check if it's using default
    def check_var(value, default):
        if value == default:
            return f"{value} (default)"
        else:
            return f"{value} (set by user)"
    
    for var, default in DEFAULTS.items():
        value = globals().get(var)
        logger.info(f"{var}: {check_var(value, default)}")

# Call the function to print out the environment variables on startup
print_environment_variables()

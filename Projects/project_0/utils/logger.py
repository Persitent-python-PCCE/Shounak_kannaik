import logging
import os

# Configure the root logger
log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Export a configured logger instance
logger = logging.getLogger('EZBuyApp')

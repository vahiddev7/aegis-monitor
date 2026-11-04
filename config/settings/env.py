import os
import environ

# Create Env instance
env = environ.Env(
    DEBUG=(bool, False)
)

# Path to the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(BASE_DIR, ".env")

# Read env file
environ.Env.read_env(ENV_FILE)

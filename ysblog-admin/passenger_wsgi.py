"""Entry point for GoDaddy cPanel "Setup Python App" (Phusion Passenger)."""
from app import create_app

application = create_app()

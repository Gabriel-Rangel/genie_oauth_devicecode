"""
Genie AI Chatbot - Modular Components

This package contains the modular components for the Genie AI Chatbot:
- auth_handler: Azure OAuth2 authentication
- genie_client: Databricks Genie API integration
- response_formatter: Data formatting utilities
- ui_components: User interface components
- config: Configuration management
"""

from .auth_handler import AzureAuthHandler
from .genie_client import GenieClient
from .response_formatter import ResponseFormatter
from .ui_components import UIComponents
from .config import Config

__all__ = [
    'AzureAuthHandler',
    'GenieClient', 
    'ResponseFormatter',
    'UIComponents',
    'Config'
]

__version__ = "1.0.0"

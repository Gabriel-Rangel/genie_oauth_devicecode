"""
Configuration settings for the Genie AI Chatbot
"""
import os
from typing import Dict, Any


class Config:
    """Configuration management for the application"""
    
    # Azure OAuth settings
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    SCOPE = os.getenv("SCOPE", "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
    
    # Databricks settings
    DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
    GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")
    
    # Application settings
    MAX_DISPLAY_ROWS = 20
    DEFAULT_WAIT_TIME = 60
    
    # UI settings
    SAMPLE_QUESTIONS = [
        "Mostre dados de exemplo",
        "Quantos registros existem?",
        "Qual é a estrutura dos dados?",
        "Explique o conjunto de dados",
        "Quais colunas estão disponíveis?",
        "Mostre dados recentes",
        "Qual é o resumo?",
        "Descreva os dados"
    ]
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate that all required configuration is present"""
        required_vars = [
            'TENANT_ID', 'CLIENT_ID',
            'DATABRICKS_HOST', 'GENIE_SPACE_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        return {
            'valid': len(missing_vars) == 0,
            'missing_vars': missing_vars
        }
    
    @classmethod
    def get_azure_config(cls) -> Dict[str, str]:
        """Get Azure-specific configuration"""
        return {
            'tenant_id': cls.TENANT_ID,
            'client_id': cls.CLIENT_ID,
            'scope': cls.SCOPE
        }
    
    @classmethod
    def get_databricks_config(cls) -> Dict[str, str]:
        """Get Databricks-specific configuration"""
        return {
            'host': cls.DATABRICKS_HOST,
            'space_id': cls.GENIE_SPACE_ID
        }

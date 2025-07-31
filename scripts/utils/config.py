# =============================================================================
# SERENA SDR - CONFIG UTILS
# =============================================================================

"""
Configuration Utilities

Este módulo gerencia as configurações e variáveis de ambiente do sistema Serena SDR.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SDRConfig:
    """Configurações do sistema Serena SDR."""
    
    # OpenAI Configuration
    openai_api_key: str
    supabase_mcp_url: str
    serena_mcp_url: str
    whatsapp_mcp_url: str
    serena_api_token: str
    whatsapp_api_token: str
    
    # OpenAI Configuration (com valores padrão)
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 1500
    openai_temperature: float = 0.5
    
    # Serena API Configuration (com valores padrão)
    serena_api_endpoint: str = "https://partnership-service-staging.api.srna.co/"
    
    # WhatsApp Configuration (com valores padrão)
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: str = ""
    
    # Performance Configuration
    max_retries: int = 3
    request_timeout: int = 30
    context_size_limit: int = 102400
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Business Rules
    min_invoice_amount: float = 200.0  # Valor mínimo para qualificação
    follow_up_delay_hours: int = 2  # Delay para follow-up em horas
    
    @classmethod
    def from_env(cls) -> 'SDRConfig':
        """Cria configuração a partir de variáveis de ambiente."""
        
        # OpenAI
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrado")
        
        # MCP URLs
        supabase_mcp_url = os.getenv('SUPABASE_MCP_URL')
        if not supabase_mcp_url:
            raise ValueError("SUPABASE_MCP_URL não encontrado")
        
        serena_mcp_url = os.getenv('SERENA_MCP_URL')
        if not serena_mcp_url:
            raise ValueError("SERENA_MCP_URL não encontrado")
        
        whatsapp_mcp_url = os.getenv('WHATSAPP_MCP_URL')
        if not whatsapp_mcp_url:
            raise ValueError("WHATSAPP_MCP_URL não encontrado")
        
        # Serena API
        serena_api_token = os.getenv('SERENA_API_TOKEN')
        if not serena_api_token:
            raise ValueError("SERENA_API_TOKEN não encontrado")
        
        # WhatsApp
        whatsapp_api_token = os.getenv('WHATSAPP_API_TOKEN')
        if not whatsapp_api_token:
            raise ValueError("WHATSAPP_API_TOKEN não encontrado")
        
        whatsapp_phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        whatsapp_business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
        
        return cls(
            openai_api_key=openai_api_key,
            openai_model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            openai_max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1500')),
            openai_temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.5')),
            
            supabase_mcp_url=supabase_mcp_url,
            serena_mcp_url=serena_mcp_url,
            whatsapp_mcp_url=whatsapp_mcp_url,
            
            serena_api_token=serena_api_token,
            serena_api_endpoint=os.getenv('SERENA_API_ENDPOINT', 'https://partnership-service-staging.api.srna.co/'),
            
            whatsapp_api_token=whatsapp_api_token,
            whatsapp_phone_number_id=whatsapp_phone_number_id,
            whatsapp_business_account_id=whatsapp_business_account_id,
            
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            context_size_limit=int(os.getenv('CONTEXT_SIZE_LIMIT', '102400')),
            
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            
            min_invoice_amount=float(os.getenv('MIN_INVOICE_AMOUNT', '200.0')),
            follow_up_delay_hours=int(os.getenv('FOLLOW_UP_DELAY_HOURS', '2'))
        )
    
    def validate(self) -> bool:
        """Valida se todas as configurações obrigatórias estão presentes."""
        required_fields = [
            'openai_api_key',
            'supabase_mcp_url',
            'serena_mcp_url',
            'whatsapp_mcp_url',
            'serena_api_token',
            'whatsapp_api_token'
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                logger.error(f"Campo obrigatório ausente: {field}")
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário."""
        return {
            'openai_model': self.openai_model,
            'openai_max_tokens': self.openai_max_tokens,
            'openai_temperature': self.openai_temperature,
            'supabase_mcp_url': self.supabase_mcp_url,
            'serena_mcp_url': self.serena_mcp_url,
            'whatsapp_mcp_url': self.whatsapp_mcp_url,
            'serena_api_endpoint': self.serena_api_endpoint,
            'max_retries': self.max_retries,
            'request_timeout': self.request_timeout,
            'context_size_limit': self.context_size_limit,
            'log_level': self.log_level,
            'min_invoice_amount': self.min_invoice_amount,
            'follow_up_delay_hours': self.follow_up_delay_hours
        }


class ConfigManager:
    """Gerenciador de configurações do sistema."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[SDRConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = SDRConfig.from_env()
            self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging baseado nas configurações."""
        logging.basicConfig(
            level=getattr(logging, self._config.log_level),
            format=self._config.log_format
        )
    
    @property
    def config(self) -> SDRConfig:
        """Retorna a configuração atual."""
        return self._config
    
    def reload(self) -> SDRConfig:
        """Recarrega configurações do ambiente."""
        self._config = SDRConfig.from_env()
        self._setup_logging()
        return self._config
    
    def get_mcp_url(self, service: str) -> str:
        """Retorna URL do MCP para um serviço específico."""
        mcp_urls = {
            'supabase': self._config.supabase_mcp_url,
            'serena': self._config.serena_mcp_url,
            'whatsapp': self._config.whatsapp_mcp_url
        }
        
        if service not in mcp_urls:
            raise ValueError(f"Serviço MCP desconhecido: {service}")
        
        return mcp_urls[service]
    
    def is_qualified_lead(self, invoice_amount: float) -> bool:
        """Verifica se um lead está qualificado baseado no valor da conta."""
        return invoice_amount >= self._config.min_invoice_amount
    
    def get_follow_up_delay(self) -> int:
        """Retorna o delay para follow-up em segundos."""
        return self._config.follow_up_delay_hours * 3600


# Instância global do gerenciador de configurações
config_manager = ConfigManager()


def get_config() -> SDRConfig:
    """Retorna a configuração atual do sistema."""
    return config_manager.config


def get_mcp_url(service: str) -> str:
    """Retorna URL do MCP para um serviço específico."""
    return config_manager.get_mcp_url(service)


def is_qualified_lead(invoice_amount: float) -> bool:
    """Verifica se um lead está qualificado."""
    return config_manager.is_qualified_lead(invoice_amount)


def get_follow_up_delay() -> int:
    """Retorna o delay para follow-up."""
    return config_manager.get_follow_up_delay() 
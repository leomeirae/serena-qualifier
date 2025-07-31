# =============================================================================
# SERENA SDR - LOGGER UTILS
# =============================================================================

"""
Logger Utilities

Este módulo fornece logging estruturado para o sistema Serena SDR.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback


class SDRLogger:
    """Logger personalizado para o sistema Serena SDR."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Inicializa o logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers para o logger."""
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formato para console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Handler para arquivo (se necessário)
        # file_handler = logging.FileHandler('serena_sdr.log')
        # file_handler.setLevel(logging.DEBUG)
        # file_formatter = logging.Formatter(
        #     '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        # )
        # file_handler.setFormatter(file_formatter)
        # self.logger.addHandler(file_handler)
        
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log de informação."""
        self.logger.info(self._format_message(message, **kwargs))
    
    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log de aviso."""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log de erro."""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log crítico."""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Formata mensagem com contexto adicional."""
        if kwargs:
            context = json.dumps(kwargs, ensure_ascii=False, default=str)
            return f"{message} | Context: {context}"
        return message
    
    def log_function_call(self, func_name: str, args: tuple, kwargs: dict, result: Any = None, error: Exception = None):
        """Log de chamada de função."""
        context = {
            "function": func_name,
            "args": str(args),
            "kwargs": kwargs,
            "timestamp": datetime.now().isoformat()
        }
        
        if result is not None:
            context["result"] = str(result)
        
        if error is not None:
            context["error"] = str(error)
            context["traceback"] = traceback.format_exc()
            self.error(f"Function call failed: {func_name}", **context)
        else:
            self.info(f"Function call: {func_name}", **context)
    
    def log_mcp_request(self, service: str, method: str, params: dict, response: Any = None, error: Exception = None):
        """Log de requisição MCP."""
        context = {
            "service": service,
            "method": method,
            "params": params,
            "timestamp": datetime.now().isoformat()
        }
        
        if response is not None:
            context["response"] = str(response)
        
        if error is not None:
            context["error"] = str(error)
            self.error(f"MCP request failed: {service}.{method}", **context)
        else:
            self.info(f"MCP request: {service}.{method}", **context)
    
    def log_lead_interaction(self, lead_id: str, phone: str, action: str, details: Dict[str, Any] = None):
        """Log de interação com lead."""
        context = {
            "lead_id": lead_id,
            "phone": phone,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            context.update(details)
        
        self.info(f"Lead interaction: {action}", **context)
    
    def log_ai_response(self, lead_id: str, phone: str, user_message: str, ai_response: str, processing_time: float = None):
        """Log de resposta da IA."""
        context = {
            "lead_id": lead_id,
            "phone": phone,
            "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
            "ai_response_length": len(ai_response),
            "timestamp": datetime.now().isoformat()
        }
        
        if processing_time is not None:
            context["processing_time_seconds"] = processing_time
        
        self.info(f"AI response generated", **context)
    
    def log_whatsapp_message(self, phone: str, message_type: str, content: str, success: bool, error: str = None):
        """Log de mensagem WhatsApp."""
        context = {
            "phone": phone,
            "message_type": message_type,
            "content_length": len(content),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            context["error"] = error
        
        if success:
            self.info(f"WhatsApp message sent", **context)
        else:
            self.error(f"WhatsApp message failed", **context)
    
    def log_ocr_processing(self, image_url: str, extracted_data: Dict[str, Any], confidence: float, success: bool):
        """Log de processamento OCR."""
        context = {
            "image_url": image_url,
            "extracted_fields": list(extracted_data.keys()),
            "confidence": confidence,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.info(f"OCR processing completed", **context)
        else:
            self.error(f"OCR processing failed", **context)


def get_logger(name: str) -> SDRLogger:
    """Retorna uma instância do logger."""
    return SDRLogger(name)


def log_function_calls(logger: SDRLogger):
    """Decorator para log automático de chamadas de função."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                logger.log_function_call(
                    func.__name__,
                    args,
                    kwargs,
                    result=result
                )
                
                return result
            except Exception as e:
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                logger.log_function_call(
                    func.__name__,
                    args,
                    kwargs,
                    error=e
                )
                raise
        return wrapper
    return decorator


def log_mcp_calls(logger: SDRLogger):
    """Decorator para log automático de chamadas MCP."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Tentar extrair informações da chamada
                service = "unknown"
                method = func.__name__
                
                if len(args) > 0:
                    service = str(args[0])
                
                logger.log_mcp_request(
                    service,
                    method,
                    kwargs,
                    response=result
                )
                
                return result
            except Exception as e:
                logger.log_mcp_request(
                    "unknown",
                    func.__name__,
                    kwargs,
                    error=e
                )
                raise
        return wrapper
    return decorator


# Loggers específicos para diferentes componentes
def get_agent_logger() -> SDRLogger:
    """Logger para o agente conversacional."""
    return get_logger("serena_sdr.agent")


def get_supabase_logger() -> SDRLogger:
    """Logger para operações Supabase."""
    return get_logger("serena_sdr.supabase")


def get_serena_logger() -> SDRLogger:
    """Logger para operações Serena API."""
    return get_logger("serena_sdr.serena")


def get_whatsapp_logger() -> SDRLogger:
    """Logger para operações WhatsApp."""
    return get_logger("serena_sdr.whatsapp")


def get_ocr_logger() -> SDRLogger:
    """Logger para operações OCR."""
    return get_logger("serena_sdr.ocr")


def get_workflow_logger() -> SDRLogger:
    """Logger para operações do workflow."""
    return get_logger("serena_sdr.workflow")


# Funções de conveniência para logging rápido
def log_lead_created(lead_id: str, phone: str, name: str = None):
    """Log de lead criado."""
    logger = get_agent_logger()
    details = {"name": name} if name else {}
    logger.log_lead_interaction(lead_id, phone, "lead_created", details)


def log_lead_qualified(lead_id: str, phone: str, invoice_amount: float):
    """Log de lead qualificado."""
    logger = get_agent_logger()
    details = {"invoice_amount": invoice_amount}
    logger.log_lead_interaction(lead_id, phone, "lead_qualified", details)


def log_message_sent(phone: str, message: str, success: bool = True, error: str = None):
    """Log de mensagem enviada."""
    logger = get_whatsapp_logger()
    logger.log_whatsapp_message(phone, "text", message, success, error)


def log_bill_processed(image_url: str, extracted_data: Dict[str, Any], confidence: float):
    """Log de fatura processada."""
    logger = get_ocr_logger()
    logger.log_ocr_processing(image_url, extracted_data, confidence, True)


def log_ai_conversation(lead_id: str, phone: str, user_message: str, ai_response: str, processing_time: float = None):
    """Log de conversa com IA."""
    logger = get_agent_logger()
    logger.log_ai_response(lead_id, phone, user_message, ai_response, processing_time) 
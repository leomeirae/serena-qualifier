# =============================================================================
# SERENA SDR - MEDIA CLASSIFICATION
# =============================================================================

"""
Media Classification Script

Este script classifica o tipo de mídia recebida via WhatsApp
e determina se é uma fatura de energia ou outro tipo de documento.

Funcionalidades:
- Classificação de imagens usando OpenAI Vision
- Detecção de faturas de energia
- Extração de informações básicas
- Logging de classificações

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
import openai
from typing import Dict, Any, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("serena_sdr.media_classification")


def classify_media_content(media_id: str, message_type: str, message_text: str) -> Dict[str, Any]:
    """
    Classifica o tipo de mídia recebida.
    
    Args:
        media_id: ID da mídia do WhatsApp
        message_type: Tipo da mensagem (text, image, etc.)
        message_text: Texto da mensagem (se houver)
        
    Returns:
        Dict com informações da classificação
    """
    try:
        logger.info(f"Classificando mídia: media_id={media_id}, type={message_type}")
        
        # Se não há media_id, é texto
        if not media_id or media_id.strip() == "":
            return {
                "is_image": False,
                "confidence": 1.0,
                "extracted_text": message_text,
                "classification": "text",
                "reasoning": "Sem media_id, mensagem de texto"
            }
        
        # Se message_type é image, é imagem
        if message_type == "image":
            return {
                "is_image": True,
                "confidence": 0.9,
                "extracted_text": "",
                "classification": "image",
                "reasoning": "Message type é 'image'"
            }
        
        # Se message_type é text, é texto
        if message_type == "text":
            return {
                "is_image": False,
                "confidence": 1.0,
                "extracted_text": message_text,
                "classification": "text",
                "reasoning": "Message type é 'text'"
            }
        
        # Para outros tipos, assumir texto
        return {
            "is_image": False,
            "confidence": 0.8,
            "extracted_text": message_text,
            "classification": "unknown",
            "reasoning": f"Tipo desconhecido: {message_type}, assumindo texto"
        }
        
    except Exception as e:
        logger.error(f"Erro na classificação de mídia: {str(e)}")
        return {
            "is_image": False,
            "confidence": 0.0,
            "extracted_text": "",
            "classification": "error",
            "reasoning": f"Erro na classificação: {str(e)}"
        }


class MediaClassifier:
    """Classificador de mídia para o sistema Serena SDR."""
    
    def __init__(self):
        """Inicializa o classificador de mídia."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Configurar OpenAI
        self.model = "gpt-4-vision-preview"
        self.max_tokens = 500
        self.temperature = 0.1
        
        logger.info("Media Classifier inicializado")
    
    def classify_media(self, image_url: str, media_id: str = None) -> Dict[str, Any]:
        """
        Classifica o tipo de mídia recebida.
        
        Args:
            image_url: URL da imagem para classificar
            media_id: ID da mídia do WhatsApp
            
        Returns:
            Dict com informações da classificação
        """
        try:
            logger.info(f"Classificando mídia: {image_url}")
            
            # Prompt para classificação
            system_prompt = """
            Você é um classificador especializado em documentos de energia.
            
            Analise a imagem e classifique o tipo de documento:
            
            TIPOS POSSÍVEIS:
            - "energy_bill": Fatura de energia elétrica
            - "other_document": Outro tipo de documento
            - "not_document": Não é um documento (foto pessoal, etc.)
            
            Para faturas de energia, extraia:
            - Valor total da fatura
            - Data de vencimento
            - Consumo em kWh
            - Nome da distribuidora
            
            Responda em JSON com a seguinte estrutura:
            {
                "classification": "energy_bill|other_document|not_document",
                "confidence": 0.95,
                "extracted_data": {
                    "total_value": 150.50,
                    "due_date": "2024-01-15",
                    "consumption_kwh": 250,
                    "utility_name": "ENEL SP"
                },
                "reasoning": "Explicação da classificação"
            }
            """
            
            # Chamar OpenAI Vision
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Classifique esta imagem e extraia informações se for uma fatura de energia:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Processar resposta
            content = response.choices[0].message.content
            
            try:
                # Tentar extrair JSON da resposta
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                else:
                    json_str = content.strip()
                
                result = json.loads(json_str)
                
            except json.JSONDecodeError:
                # Fallback se não conseguir extrair JSON
                logger.warning("Não foi possível extrair JSON da resposta, usando fallback")
                result = {
                    "classification": "other_document",
                    "confidence": 0.5,
                    "extracted_data": {},
                    "reasoning": "Erro na extração de dados"
                }
            
            # Adicionar metadados
            result.update({
                "media_id": media_id,
                "image_url": image_url,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model
            })
            
            logger.info(f"Classificação concluída: {result['classification']} (confiança: {result['confidence']})")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na classificação de mídia: {str(e)}")
            return {
                "classification": "error",
                "confidence": 0.0,
                "extracted_data": {},
                "reasoning": f"Erro na classificação: {str(e)}",
                "media_id": media_id,
                "image_url": image_url,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def is_energy_bill(self, classification_result: Dict[str, Any]) -> bool:
        """
        Verifica se a classificação indica uma fatura de energia.
        
        Args:
            classification_result: Resultado da classificação
            
        Returns:
            bool: True se for fatura de energia
        """
        return (
            classification_result.get("classification") == "energy_bill" and
            classification_result.get("confidence", 0) > 0.7
        )
    
    def get_extracted_data(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai dados da fatura de energia.
        
        Args:
            classification_result: Resultado da classificação
            
        Returns:
            Dict com dados extraídos
        """
        if self.is_energy_bill(classification_result):
            return classification_result.get("extracted_data", {})
        return {}
    
    def log_classification(self, classification_result: Dict[str, Any], phone_number: str = None):
        """
        Registra a classificação no log.
        
        Args:
            classification_result: Resultado da classificação
            phone_number: Número do telefone do lead
        """
        log_data = {
            "phone_number": phone_number,
            "media_id": classification_result.get("media_id"),
            "classification": classification_result.get("classification"),
            "confidence": classification_result.get("confidence"),
            "timestamp": classification_result.get("timestamp"),
            "is_energy_bill": self.is_energy_bill(classification_result)
        }
        
        logger.info("Classificação de mídia registrada", extra=log_data)


def main():
    """Função principal para testes."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python classify_media.py <image_url> [media_id]")
        sys.exit(1)
    
    image_url = sys.argv[1]
    media_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    classifier = MediaClassifier()
    result = classifier.classify_media(image_url, media_id)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main() 
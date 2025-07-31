#!/usr/bin/env python3
# =============================================================================
# SERENA SDR - MONITORAMENTO AUTOMÁTICO DE MCP SERVERS
# =============================================================================

"""
Script de monitoramento automático para os MCP servers.

Este script:
1. Monitora healthchecks dos MCPs a cada hora
2. Envia notificações em caso de falha
3. Gera relatórios de status
4. Pode ser executado como job Kestra ou cron

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import requests
import json
import time
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MCPServerMonitor:
    """Monitor de MCP Servers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.mcp_servers = {
            "supabase": {
                "url": "http://supabase-mcp-server:3000",
                "health_endpoint": "/health",
                "description": "Supabase MCP Server",
                "critical": True
            },
            "serena": {
                "url": "http://serena-mcp-server:3002",
                "health_endpoint": "/health",
                "description": "Serena MCP Server",
                "critical": True
            },
            "whatsapp": {
                "url": "http://whatsapp-mcp-server:3003",
                "health_endpoint": "/health",
                "description": "WhatsApp MCP Server",
                "critical": True
            }
        }
        
        self.status_history = {}
        self.failure_count = {}
        self.last_notification = {}
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/mcp_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Carrega configuração padrão."""
        return {
            "check_interval": 3600,  # 1 hora
            "timeout": 10,
            "retry_attempts": 3,
            "notification_cooldown": 3600,  # 1 hora entre notificações
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "monitor@serena.com",
                "password": "your_password",
                "recipients": ["admin@serena.com"]
            },
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/..."
            }
        }
    
    def check_server_health(self, server_name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica saúde de um MCP server."""
        health_url = f"{server_config['url']}{server_config['health_endpoint']}"
        
        for attempt in range(self.config["retry_attempts"]):
            try:
                response = requests.get(
                    health_url, 
                    timeout=self.config["timeout"]
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except requests.exceptions.ConnectionError:
                if attempt == self.config["retry_attempts"] - 1:
                    return {
                        "status": "unhealthy",
                        "error": "Connection refused",
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(1)
                
            except requests.exceptions.Timeout:
                if attempt == self.config["retry_attempts"] - 1:
                    return {
                        "status": "unhealthy",
                        "error": "Timeout",
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(1)
                
            except Exception as e:
                if attempt == self.config["retry_attempts"] - 1:
                    return {
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                time.sleep(1)
        
        return {
            "status": "unknown",
            "error": "Max retry attempts exceeded",
            "timestamp": datetime.now().isoformat()
        }
    
    def should_send_notification(self, server_name: str) -> bool:
        """Verifica se deve enviar notificação para um servidor."""
        if server_name not in self.last_notification:
            return True
        
        last_notif = self.last_notification[server_name]
        cooldown = timedelta(seconds=self.config["notification_cooldown"])
        
        return datetime.now() - last_notif > cooldown
    
    def send_email_notification(self, subject: str, body: str) -> bool:
        """Envia notificação por email."""
        if not self.config["email"]["enabled"]:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["username"]
            msg['To'] = ", ".join(self.config["email"]["recipients"])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.config["email"]["smtp_server"], 
                self.config["email"]["smtp_port"]
            )
            server.starttls()
            server.login(
                self.config["email"]["username"], 
                self.config["email"]["password"]
            )
            
            text = msg.as_string()
            server.sendmail(
                self.config["email"]["username"], 
                self.config["email"]["recipients"], 
                text
            )
            server.quit()
            
            self.logger.info(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def send_slack_notification(self, message: str) -> bool:
        """Envia notificação para Slack."""
        if not self.config["slack"]["enabled"]:
            return False
        
        try:
            payload = {"text": message}
            response = requests.post(
                self.config["slack"]["webhook_url"],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Slack notification sent")
                return True
            else:
                self.logger.error(f"Failed to send Slack notification: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
            return False
    
    def generate_status_report(self) -> str:
        """Gera relatório de status."""
        report = []
        report.append("=" * 60)
        report.append("📊 RELATÓRIO DE MONITORAMENTO MCP SERVERS")
        report.append("=" * 60)
        report.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_servers = len(self.mcp_servers)
        healthy_servers = sum(
            1 for result in self.status_history.values() 
            if result.get("status") == "healthy"
        )
        
        report.append(f"📈 Status Geral: {healthy_servers}/{total_servers} servidores saudáveis")
        report.append("")
        
        for server_name, result in self.status_history.items():
            server_config = self.mcp_servers[server_name]
            report.append(f"🔗 {server_config['description']}")
            report.append(f"   Status: {'✅ Saudável' if result.get('status') == 'healthy' else '❌ Problema'}")
            report.append(f"   Última verificação: {result.get('timestamp', 'N/A')}")
            
            if result.get("status") == "healthy":
                response_time = result.get("response_time", 0)
                report.append(f"   Tempo de resposta: {response_time:.3f}s")
            else:
                error = result.get("error", "Erro desconhecido")
                report.append(f"   Erro: {error}")
            
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Executa um ciclo completo de monitoramento."""
        self.logger.info("Iniciando ciclo de monitoramento MCP servers")
        
        current_status = {}
        failed_servers = []
        
        # Verificar cada servidor
        for server_name, server_config in self.mcp_servers.items():
            self.logger.info(f"Verificando {server_config['description']}")
            
            result = self.check_server_health(server_name, server_config)
            current_status[server_name] = result
            self.status_history[server_name] = result
            
            if result["status"] != "healthy":
                failed_servers.append(server_name)
                self.failure_count[server_name] = self.failure_count.get(server_name, 0) + 1
                
                # Enviar notificação se necessário
                if self.should_send_notification(server_name):
                    self._send_failure_notification(server_name, server_config, result)
                    self.last_notification[server_name] = datetime.now()
            else:
                # Reset failure count se saudável
                self.failure_count[server_name] = 0
        
        # Gerar relatório
        report = self.generate_status_report()
        self.logger.info(f"Ciclo concluído. {len(failed_servers)} servidores com problemas")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "healthy_count": len(self.mcp_servers) - len(failed_servers),
            "total_count": len(self.mcp_servers),
            "failed_servers": failed_servers,
            "report": report,
            "status": current_status
        }
    
    def _send_failure_notification(self, server_name: str, server_config: Dict[str, Any], result: Dict[str, Any]):
        """Envia notificação de falha."""
        subject = f"🚨 ALERTA: MCP Server {server_config['description']} com problema"
        
        body = f"""
ALERTA DE MONITORAMENTO MCP SERVER

Servidor: {server_config['description']}
URL: {server_config['url']}
Status: {result['status']}
Erro: {result.get('error', 'N/A')}
Timestamp: {result.get('timestamp', 'N/A')}

Contador de falhas: {self.failure_count.get(server_name, 0)}

Ação recomendada:
1. Verificar logs do servidor
2. Verificar conectividade de rede
3. Reiniciar serviço se necessário
4. Verificar variáveis de ambiente

---
Monitoramento Automático Serena SDR
"""
        
        # Enviar notificações
        self.send_email_notification(subject, body)
        self.send_slack_notification(f"🚨 {subject}\n{body}")
    
    def run_continuous_monitoring(self):
        """Executa monitoramento contínuo."""
        self.logger.info("Iniciando monitoramento contínuo MCP servers")
        
        while True:
            try:
                result = self.run_monitoring_cycle()
                
                # Aguardar próximo ciclo
                self.logger.info(f"Aguardando {self.config['check_interval']} segundos até próximo ciclo")
                time.sleep(self.config["check_interval"])
                
            except KeyboardInterrupt:
                self.logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"Erro durante monitoramento: {str(e)}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de MCP Servers")
    parser.add_argument("--once", action="store_true", help="Executar apenas uma vez")
    parser.add_argument("--config", help="Arquivo de configuração JSON")
    parser.add_argument("--interval", type=int, default=3600, help="Intervalo de verificação em segundos")
    
    args = parser.parse_args()
    
    # Carregar configuração
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configuração: {str(e)}")
            return
    
    # Ajustar intervalo se especificado
    if args.interval != 3600:
        if config is None:
            config = {}
        config["check_interval"] = args.interval
    
    # Criar monitor
    monitor = MCPServerMonitor(config)
    
    if args.once:
        # Executar apenas uma vez
        result = monitor.run_monitoring_cycle()
        print(result["report"])
    else:
        # Executar monitoramento contínuo
        monitor.run_continuous_monitoring()


if __name__ == "__main__":
    main() 
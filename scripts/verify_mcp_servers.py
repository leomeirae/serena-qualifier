#!/usr/bin/env python3
# =============================================================================
# SERENA SDR - VERIFICAÇÃO DE MCP SERVERS
# =============================================================================

"""
Script para verificar se os MCP servers estão funcionando corretamente.

Este script testa:
1. Healthchecks dos MCPs
2. Conectividade entre serviços
3. Funcionalidade básica dos MCPs

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List


class MCPServerVerifier:
    """Verificador de MCP Servers."""
    
    def __init__(self):
        self.mcp_servers = {
            "supabase": {
                "url": "http://supabase-mcp-server:3000",
                "health_endpoint": "/health",
                "description": "Supabase MCP Server"
            },
            "serena": {
                "url": "http://serena-mcp-server:3002",
                "health_endpoint": "/health",
                "description": "Serena MCP Server"
            },
            "whatsapp": {
                "url": "http://whatsapp-mcp-server:3003",
                "health_endpoint": "/health",
                "description": "WhatsApp MCP Server"
            }
        }
        
        self.results = {}
    
    def test_health_check(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Testa o health check de um MCP server."""
        try:
            health_url = f"{server_config['url']}{server_config['health_endpoint']}"
            print(f"🔍 Testando health check: {health_url}")
            
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {server_config['description']} - Status: {data.get('status', 'unknown')}")
                self.results[server_name] = {
                    "health_check": True,
                    "status_code": response.status_code,
                    "response": data
                }
                return True
            else:
                print(f"❌ {server_config['description']} - Status Code: {response.status_code}")
                self.results[server_name] = {
                    "health_check": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {server_config['description']} - Erro de conexão")
            self.results[server_name] = {
                "health_check": False,
                "error": "Connection refused"
            }
            return False
        except requests.exceptions.Timeout:
            print(f"❌ {server_config['description']} - Timeout")
            self.results[server_name] = {
                "health_check": False,
                "error": "Timeout"
            }
            return False
        except Exception as e:
            print(f"❌ {server_config['description']} - Erro: {str(e)}")
            self.results[server_name] = {
                "health_check": False,
                "error": str(e)
            }
            return False
    
    def test_mcp_functionality(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Testa funcionalidade básica do MCP server."""
        try:
            # Teste básico de JSON-RPC
            test_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            print(f"🔍 Testando funcionalidade MCP: {server_config['url']}")
            
            response = requests.post(
                f"{server_config['url']}/mcp",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools_count = len(data["result"]["tools"])
                    print(f"✅ {server_config['description']} - {tools_count} tools disponíveis")
                    self.results[server_name]["mcp_functionality"] = True
                    self.results[server_name]["tools_count"] = tools_count
                    return True
                else:
                    print(f"⚠️ {server_config['description']} - Resposta inválida")
                    self.results[server_name]["mcp_functionality"] = False
                    self.results[server_name]["error"] = "Invalid response format"
                    return False
            else:
                print(f"❌ {server_config['description']} - Status Code: {response.status_code}")
                self.results[server_name]["mcp_functionality"] = False
                self.results[server_name]["error"] = f"HTTP {response.status_code}"
                return False
                
        except Exception as e:
            print(f"❌ {server_config['description']} - Erro: {str(e)}")
            self.results[server_name]["mcp_functionality"] = False
            self.results[server_name]["error"] = str(e)
            return False
    
    def test_connectivity(self) -> bool:
        """Testa conectividade entre serviços."""
        print("\n🌐 Testando conectividade entre serviços...")
        
        all_healthy = True
        
        for server_name, server_config in self.mcp_servers.items():
            print(f"\n📡 Testando {server_config['description']}...")
            
            # Teste de health check
            health_ok = self.test_health_check(server_name, server_config)
            
            # Teste de funcionalidade MCP (apenas se health check passar)
            if health_ok:
                mcp_ok = self.test_mcp_functionality(server_name, server_config)
                if not mcp_ok:
                    all_healthy = False
            else:
                all_healthy = False
            
            print(f"📊 Resultado: {'✅ OK' if health_ok else '❌ FALHOU'}")
        
        return all_healthy
    
    def generate_report(self) -> str:
        """Gera relatório dos testes."""
        report = []
        report.append("=" * 60)
        report.append("📊 RELATÓRIO DE VERIFICAÇÃO DOS MCP SERVERS")
        report.append("=" * 60)
        
        total_servers = len(self.mcp_servers)
        healthy_servers = sum(1 for result in self.results.values() if result.get("health_check", False))
        
        report.append(f"📈 Resumo: {healthy_servers}/{total_servers} servidores saudáveis")
        report.append("")
        
        for server_name, result in self.results.items():
            server_config = self.mcp_servers[server_name]
            report.append(f"🔗 {server_config['description']}")
            report.append(f"   URL: {server_config['url']}")
            
            if result.get("health_check", False):
                report.append(f"   ✅ Health Check: OK")
                if result.get("mcp_functionality", False):
                    report.append(f"   ✅ Funcionalidade MCP: OK ({result.get('tools_count', 0)} tools)")
                else:
                    report.append(f"   ❌ Funcionalidade MCP: FALHOU")
            else:
                report.append(f"   ❌ Health Check: FALHOU")
                if "error" in result:
                    report.append(f"   💥 Erro: {result['error']}")
            
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    def run_verification(self) -> bool:
        """Executa verificação completa."""
        print("🚀 Iniciando verificação dos MCP Servers...")
        print("=" * 60)
        
        success = self.test_connectivity()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 TODOS OS MCP SERVERS ESTÃO FUNCIONANDO CORRETAMENTE!")
        else:
            print("⚠️ ALGUNS MCP SERVERS ESTÃO COM PROBLEMAS!")
        print("=" * 60)
        
        # Gerar relatório
        report = self.generate_report()
        print(report)
        
        return success


def main():
    """Função principal."""
    print("🔧 SERENA SDR - VERIFICAÇÃO DE MCP SERVERS")
    print("=" * 60)
    
    verifier = MCPServerVerifier()
    
    try:
        success = verifier.run_verification()
        
        if success:
            print("\n✅ Verificação concluída com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Verificação falhou!")
            print("\n🔧 Comandos para troubleshooting:")
            print("docker-compose ps")
            print("docker-compose logs supabase-mcp-server")
            print("docker-compose logs serena-mcp-server")
            print("docker-compose logs whatsapp-mcp-server")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Verificação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro durante verificação: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
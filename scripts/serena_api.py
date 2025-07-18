"""
Módulo para integração com a API da Serena Energia
Endpoints: /distribuited-generation/plans e /distribuited-generation/operation-areas
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import time

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerenaAPI:
    def __init__(self):
        """Inicializar cliente da API Serena"""
        self.token = os.getenv("SERENA_API_TOKEN")
        self.base_url = os.getenv("SERENA_API_BASE_URL", "https://partnership-service-staging.api.srna.co")
        
        if not self.token:
            raise ValueError("SERENA_API_TOKEN não encontrado nas variáveis de ambiente")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 segundo entre requests
        
        logger.info(f"✅ SerenaAPI inicializada com base URL: {self.base_url}")

    def _wait_rate_limit(self):
        """Implementar rate limiting básico"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"⏳ Rate limiting: aguardando {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Fazer requisição HTTP com tratamento de erros"""
        self._wait_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"🌐 {method.upper()} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            
            # Log da resposta
            logger.info(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Sucesso: {len(data) if isinstance(data, list) else 'dados'} retornados")
                return data
            
            elif response.status_code == 401:
                logger.error("🔒 Erro 401: Token de autenticação inválido")
                logger.error(f"🔑 Token usado: {self.token[:50]}...")
                logger.error(f"📋 Headers enviados: {self.headers}")
                logger.error(f"🌐 URL completa: {url}")
                logger.error(f"📄 Response body: {response.text}")
                raise Exception("Token de autenticação inválido ou expirado")
            
            elif response.status_code == 403:
                logger.error("🚫 Erro 403: Acesso negado")
                raise Exception("Acesso negado - verifique permissões")
            
            elif response.status_code == 404:
                logger.error("🔍 Erro 404: Endpoint não encontrado")
                raise Exception("Endpoint não encontrado")
            
            elif response.status_code == 429:
                logger.error("⏰ Erro 429: Rate limit excedido")
                raise Exception("Rate limit excedido - tente novamente mais tarde")
            
            else:
                logger.error(f"❌ Erro {response.status_code}: {response.text}")
                raise Exception(f"Erro na API: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout na requisição")
            raise Exception("Timeout na requisição à API Serena")
        
        except requests.exceptions.ConnectionError:
            logger.error("🌐 Erro de conexão")
            raise Exception("Erro de conexão com a API Serena")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição: {str(e)}")
            raise Exception(f"Erro na requisição: {str(e)}")

    def get_plans(self, city: Optional[str] = None, state: Optional[str] = None, 
                  energy_utility_public_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obter planos de geração distribuída
        
        Args:
            city: Nome da cidade
            state: Sigla do estado (UF) - obrigatório junto com city
            energy_utility_public_id: UUID da distribuidora (alternativa a city+state)
        
        Returns:
            Lista de planos disponíveis
        """
        try:
            query_params = {}
            
            if energy_utility_public_id:
                query_params['energy_utility_public_id'] = energy_utility_public_id
                logger.info(f"🔍 Buscando planos por distribuidora: {energy_utility_public_id}")
            elif city and state:
                query_params['city'] = city
                query_params['state'] = state
                logger.info(f"🔍 Buscando planos para: {city}/{state}")
            elif city:
                # Se só foi fornecida a cidade, tentar com estado padrão ou buscar o estado
                logger.warning(f"⚠️ Apenas cidade fornecida: {city}. Tentando inferir estado...")
                # Mapear algumas cidades comuns para estados
                city_state_map = {
                    'são paulo': 'SP', 'rio de janeiro': 'RJ', 'belo horizonte': 'MG',
                    'salvador': 'BA', 'brasília': 'DF', 'fortaleza': 'CE',
                    'recife': 'PE', 'porto alegre': 'RS', 'manaus': 'AM',
                    'curitiba': 'PR', 'goiânia': 'GO', 'vitória': 'ES'
                }
                inferred_state = city_state_map.get(city.lower())
                if inferred_state:
                    query_params['city'] = city
                    query_params['state'] = inferred_state
                    logger.info(f"🔍 Estado inferido: {city}/{inferred_state}")
                else:
                    logger.error(f"❌ Não foi possível inferir estado para: {city}")
                    return []
            else:
                logger.error("❌ Parâmetros obrigatórios: (city + state) OU energy_utility_public_id")
                return []
            
            response = self._make_request(
                method="GET",
                endpoint="/distribuited-generation/plans",
                params=query_params
            )
            
            # Processar resposta conforme documentação
            all_plans = []
            if isinstance(response, list):
                for utility_data in response:
                    if isinstance(utility_data, dict) and 'plans' in utility_data:
                        utility_name = utility_data.get('energyUtilityName', 'Distribuidora')
                        plans = utility_data.get('plans', [])
                        
                        # Adicionar nome da distribuidora aos planos
                        for plan in plans:
                            if isinstance(plan, dict):
                                plan['energyUtilityName'] = utility_name
                                all_plans.append(plan)
                
                logger.info(f"📋 Encontrados {len(all_plans)} planos total")
                return all_plans
            else:
                logger.warning("⚠️ Resposta não está no formato esperado")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar planos: {str(e)}")
            return []

    def get_operation_areas(self, state: str = None, city: str = None, ibge_code: str = None) -> List[Dict[str, Any]]:
        """
        Consultar áreas de operação de geração distribuída
        API exige: state e city OU ibge_code
        
        Args:
            state: Estado (UF)
            city: Cidade  
            ibge_code: Código IBGE da cidade
            
        Returns:
            Lista de áreas de operação
        """
        try:
            query_params = {}
            
            if ibge_code:
                query_params['ibge_code'] = ibge_code
                logger.info(f"🗺️ Buscando áreas de operação por IBGE: {ibge_code}")
            elif state and city:
                query_params['state'] = state
                query_params['city'] = city
                logger.info(f"🗺️ Buscando áreas de operação para {city}/{state}")
            else:
                # Usar valores padrão para teste
                query_params['state'] = 'SP'
                query_params['city'] = 'São Paulo'
                logger.info("🗺️ Buscando áreas de operação (usando SP/São Paulo como padrão)")
            
            areas = self._make_request(
                method="GET",
                endpoint="/distribuited-generation/operation-areas",
                params=query_params
            )
            
            if isinstance(areas, list):
                logger.info(f"📍 Encontradas {len(areas)} áreas de operação")
                return areas
            else:
                logger.warning("⚠️ Resposta não é uma lista - convertendo")
                return [areas] if areas else []
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar áreas de operação: {str(e)}")
            # Retornar lista vazia em caso de erro
            return []

    def get_plans_by_city(self, city: str, state: str = None) -> List[Dict[str, Any]]:
        """
        Buscar planos específicos para uma cidade
        Método de conveniência usado pelos workflows Kestra
        
        Args:
            city: Nome da cidade
            state: Estado (UF) - opcional, será inferido se não fornecido
            
        Returns:
            Lista de planos disponíveis para a cidade
        """
        if not city or not city.strip():
            raise ValueError("Cidade é obrigatória")
        
        city = city.strip()
        logger.info(f"🏙️ Buscando planos para cidade: {city}")
        
        try:
            plans = self.get_plans(city=city, state=state)
            
            if not plans:
                logger.warning(f"⚠️ Nenhum plano encontrado para: {city}")
                return []
            
            # Processar e formatar planos conforme documentação
            formatted_plans = []
            for plan in plans:
                if isinstance(plan, dict):
                    formatted_plan = {
                        'id': plan.get('id'),
                        'name': plan.get('name', 'Plano sem nome'),
                        'fidelityMonths': plan.get('fidelityMonths', 0),
                        'discount': plan.get('discount', '0'),
                        'energyUtilityName': plan.get('energyUtilityName', 'Distribuidora'),
                        'offeredBenefits': plan.get('offeredBenefits', []),
                        'city': city,
                        'state': state,
                        'details': plan
                    }
                    formatted_plans.append(formatted_plan)
            
            logger.info(f"✅ {len(formatted_plans)} planos formatados para {city}")
            return formatted_plans
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar planos para {city}: {str(e)}")
            # Retornar lista vazia em caso de erro para não quebrar o workflow
            return []

    def check_city_coverage(self, city: str, state: str = None) -> bool:
        """
        Verificar se uma cidade tem cobertura
        
        Args:
            city: Nome da cidade
            state: Estado (UF) - opcional, mas recomendado
            
        Returns:
            True se a cidade tem cobertura, False caso contrário
        """
        try:
            # Tentar buscar planos diretamente para a cidade
            # Se retornar planos, significa que tem cobertura
            plans = self.get_plans(city=city, state=state)
            
            if plans and len(plans) > 0:
                logger.info(f"✅ Cidade {city} tem cobertura - {len(plans)} planos disponíveis")
                return True
            
            # Tentar buscar areas de operação para verificar cobertura
            areas = self.get_operation_areas(state=state, city=city)
            if areas and len(areas) > 0:
                logger.info(f"✅ Cidade {city} tem cobertura na área de operação")
                return True
            
            logger.info(f"❌ Cidade {city} não tem cobertura")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar cobertura para {city}: {str(e)}")
            return False

# Instância global para uso nos workflows
serena_api = SerenaAPI()

# Funções de conveniência para os workflows Kestra
def get_plans_by_city(city: str) -> List[Dict[str, Any]]:
    """Função wrapper para os workflows Kestra"""
    return serena_api.get_plans_by_city(city)

def check_city_coverage(city: str) -> bool:
    """Função wrapper para verificar cobertura"""
    return serena_api.check_city_coverage(city)

def get_operation_areas(state: str = None, city: str = None, ibge_code: str = None) -> List[Dict[str, Any]]:
    """Função wrapper para áreas de operação"""
    return serena_api.get_operation_areas(state=state, city=city, ibge_code=ibge_code)


def get_lead_data_from_supabase(phone):
    """
    Buscar dados do lead no Supabase com logs detalhados para debug
    
    Args:
        phone (str): Número de telefone normalizado do lead
    
    Returns:
        dict: Dados do lead se encontrado, None caso contrário
    """
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    # Validar configurações
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Variáveis SUPABASE_URL ou SUPABASE_ANON_KEY não configuradas")
        logger.error(f"SUPABASE_URL: {'✅' if SUPABASE_URL else '❌'}")
        logger.error(f"SUPABASE_ANON_KEY: {'✅' if SUPABASE_KEY else '❌'}")
        return None
    
    # Configurar headers da requisição
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construir URL de busca
    url = f"{SUPABASE_URL}/rest/v1/leads?phone=eq.{phone}&select=*"
    
    logger.info(f"🔍 Buscando lead no Supabase")
    logger.info(f"📞 Telefone normalizado: {phone}")
    logger.info(f"🌐 URL: {url}")
    logger.info(f"🔑 Headers configurados: {list(headers.keys())}")

    try:
        # Fazer requisição com timeout
        response = requests.get(url, headers=headers, timeout=10)
        
        logger.info(f"📡 Response Status: {response.status_code}")
        logger.info(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📋 Data received: {len(data) if isinstance(data, list) else 'not a list'}")
            
            if data and len(data) > 0:
                lead_data = data[0]
                logger.info(f"✅ Lead encontrado com sucesso!")
                logger.info(f"📝 Lead ID: {lead_data.get('id', 'N/A')}")
                logger.info(f"👤 Nome: {lead_data.get('name', 'N/A')}")
                logger.info(f"📧 Email: {lead_data.get('email', 'N/A')}")
                logger.info(f"💰 Valor da fatura: R$ {lead_data.get('invoice_amount', 'N/A')}")
                return lead_data
            else:
                logger.warning(f"⚠️ Lead com telefone {phone} não encontrado no Supabase")
                logger.warning(f"📊 Resposta vazia: {data}")
                return None
                
        elif response.status_code == 401:
            logger.error("🔒 Erro 401: Token de autenticação inválido")
            logger.error("Verifique se SUPABASE_ANON_KEY está correto")
            return None
            
        elif response.status_code == 404:
            logger.error("🔍 Erro 404: Tabela 'leads' não encontrada")
            logger.error("Verifique se a tabela existe no Supabase")
            return None
            
        else:
            logger.error(f"❌ Erro na chamada Supabase: {response.status_code}")
            logger.error(f"📄 Response body: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("⏰ Timeout na requisição ao Supabase")
        return None
        
    except requests.exceptions.ConnectionError:
        logger.error("🌐 Erro de conexão com o Supabase")
        logger.error("Verifique se SUPABASE_URL está correto e acessível")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao buscar lead no Supabase: {str(e)}")
        logger.error(f"🔍 Tipo do erro: {type(e).__name__}")
        return None

if __name__ == "__main__":
    # Teste básico
    try:
        print("🧪 TESTE DA API SERENA")
        print("=" * 50)
        
        # Teste 1: Áreas de operação
        print("\n1️⃣ Testando áreas de operação...")
        areas = get_operation_areas(state="SP", city="São Paulo")
        print(f"✅ {len(areas)} áreas encontradas")
        
        # Teste 2: Planos para São Paulo
        print("\n2️⃣ Testando planos para São Paulo...")
        all_plans = serena_api.get_plans(city="São Paulo", state="SP")
        print(f"✅ {len(all_plans)} planos encontrados")
        
        # Teste 3: Planos por cidade (exemplo)
        test_cities = ["São Paulo", "Rio de Janeiro", "Belo Horizonte"]
        for city in test_cities:
            print(f"\n3️⃣ Testando planos para {city}...")
            city_plans = get_plans_by_city(city)
            coverage = check_city_coverage(city)
            print(f"✅ {len(city_plans)} planos | Cobertura: {coverage}")
        
        print("\n🎉 Todos os testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}") 
import dagster as dg
from dagster import resource
from dagster_duckdb import DuckDBResource
from orchestration.llm.llm_service import LLMService
import os
from clickhouse_connect import get_client

class ClickHouseResource(dg.ConfigurableResource):
  host: str
  port: int
  username: str
  password: str
  database: str

  def get_client(self):
    return get_client(
      host=self.host,
      port=self.port,
      username=self.username,
      password=self.password,
      database=self.database
    )
  
  def execute_query(self, query: str):
    with self.get_client() as client:
      return client.query(query)


@dg.resource(config_schema={
    'api_base': str,
    'api_key': str,
    'model': str,
    'batch_size': int,
    'max_concurrent_requests': int,
    'timeout': float
})
def llm_resource(context):
  """Ressource LLMService pour Dagster"""
  config = {
    'api_base': context.resource_config['api_base'],
    'api_key': context.resource_config['api_key'],
    'model': context.resource_config['model'],
    'batch_size': context.resource_config['batch_size'],
    'max_concurrent_requests': context.resource_config['max_concurrent_requests'],
    'timeout': context.resource_config['timeout']
  }
  
  context.log.info(f"🔄 Initialisation du LLMService avec la config: {config['model']}")
  context.log.debug(f"Configuration détaillée: {config}")
  return LLMService(config)

# Configuration avec les variables d'environnement
llm_resource_configured = llm_resource.configured({
  'api_base':   os.getenv('LLM_API_BASE'),
  'api_key':    os.getenv('LLM_API_KEY'),
  'model':      os.getenv('LLM_MODEL'),
  'batch_size': int(os.getenv('LLM_BATCH_SIZE', 8)),
  'max_concurrent_requests': int(os.getenv('LLM_MAX_CONCURRENT_REQUESTS', 4)),
  'timeout':    float(os.getenv('LLM_TIMEOUT', 30.0)),
})

clickhouse_resource = ClickHouseResource(
  host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
  port=int(os.getenv("CLICKHOUSE_PORT", 18123)),
  username=os.getenv("CLICKHOUSE_USERNAME", "default"),
  password=os.getenv("CLICKHOUSE_PASSWORD", "changeme"),
  database=os.getenv("CLICKHOUSE_DATABASE", "wtat_dw")
)

database_resource = DuckDBResource(
  database = dg.EnvVar("DUCKDB_DATABASE")
)

@dg.definitions
def resources() -> dg.Definitions:
  return dg.Definitions(resources={
    "database": database_resource,
    "llm": llm_resource_configured,
    "clickhouse": clickhouse_resource
  })

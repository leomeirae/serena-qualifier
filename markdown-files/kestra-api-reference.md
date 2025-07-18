# Kestra Open Source API Documentation

## Overview

The Kestra Open Source API provides comprehensive functionality for managing workflows, executions, logs, and system resources through a RESTful interface. This documentation covers all available endpoints organized by category, with detailed information about request parameters, response formats, and usage examples[1][2][3].

## Base URL and Authentication

**Base URL:** `http://localhost:8080/api/v1`

**Authentication:** For basic authentication (when enabled), use the `-u` parameter with username:password format:

```bash
curl -X POST -u '[email protected]:kestra' http://localhost:8080/api/v1/executions/company.team/hello_world
```

## API Categories

### Flows API

The Flows API manages workflow definitions, including creation, validation, and execution management[2].

#### Core Flow Operations

**Create Flow**
- `POST /api/v1/flows`
- Content-Type: `application/x-yaml`
- Creates a new flow from YAML definition

**Bulk Flow Operations**
- `POST /api/v1/flows/bulk` - Bulk create flows
- `DELETE /api/v1/flows/delete/by-ids` - Delete multiple flows by IDs
- `DELETE /api/v1/flows/delete/by-query` - Delete flows by query

**Flow State Management**
- `POST /api/v1/flows/disable/by-ids` - Disable flows by IDs
- `POST /api/v1/flows/disable/by-query` - Disable flows by query
- `POST /api/v1/flows/enable/by-ids` - Enable flows by IDs  
- `POST /api/v1/flows/enable/by-query` - Enable flows by query

**Flow Discovery**
- `GET /api/v1/flows/distinct-namespaces` - Get distinct namespaces
- `GET /api/v1/flows/search` - Search flows
- `GET /api/v1/flows/{namespace}` - Get flows in namespace
- `GET /api/v1/flows/{namespace}/{id}` - Get specific flow

**Flow Management**
- `PUT /api/v1/flows/{namespace}/{id}` - Update flow
- `DELETE /api/v1/flows/{namespace}/{id}` - Delete flow
- `GET /api/v1/flows/{namespace}/{id}/dependencies` - Get flow dependencies
- `GET /api/v1/flows/{namespace}/{id}/graph` - Get flow graph
- `GET /api/v1/flows/{namespace}/{id}/revisions` - Get flow revisions

**Flow Validation**
- `POST /api/v1/flows/validate` - Validate flow
- `POST /api/v1/flows/validate/task` - Validate task
- `POST /api/v1/flows/validate/trigger` - Validate trigger

**Import/Export**
- `POST /api/v1/flows/export/by-ids` - Export flows by IDs
- `GET /api/v1/flows/export/by-query` - Export flows by query
- `POST /api/v1/flows/import` - Import flows

### Templates API

The Templates API manages reusable workflow templates[2].

**Template Operations**
- `POST /api/v1/templates` - Create template
- `DELETE /api/v1/templates/delete/by-ids` - Delete templates by IDs
- `DELETE /api/v1/templates/delete/by-query` - Delete templates by query
- `GET /api/v1/templates/distinct-namespaces` - Get distinct namespaces
- `GET /api/v1/templates/search` - Search templates
- `POST /api/v1/templates/validate` - Validate template

**Template Management**
- `POST /api/v1/templates/{namespace}` - Create template in namespace
- `GET /api/v1/templates/{namespace}/{id}` - Get template
- `PUT /api/v1/templates/{namespace}/{id}` - Update template
- `DELETE /api/v1/templates/{namespace}/{id}` - Delete template

**Template Import/Export**
- `POST /api/v1/templates/export/by-ids` - Export templates by IDs
- `GET /api/v1/templates/export/by-query` - Export templates by query
- `POST /api/v1/templates/import` - Import templates

### Executions API

The Executions API handles workflow execution lifecycle management[2][4].

#### Execution Management

**Basic Execution Operations**
- `GET /api/v1/executions` - List executions
- `GET /api/v1/executions/{executionId}` - Get execution details
- `DELETE /api/v1/executions/{executionId}` - Delete execution
- `POST /api/v1/executions/{namespace}/{id}` - Trigger flow execution

**Execution State Control**
- `POST /api/v1/executions/{executionId}/change-status` - Change execution status
- `POST /api/v1/executions/{executionId}/pause` - Pause execution
- `POST /api/v1/executions/{executionId}/resume` - Resume execution
- `DELETE /api/v1/executions/{executionId}/kill` - Kill execution

**Bulk Operations**
- `DELETE /api/v1/executions/by-ids` - Delete executions by IDs
- `DELETE /api/v1/executions/by-query` - Delete executions by query
- `POST /api/v1/executions/change-status/by-ids` - Change status by IDs
- `POST /api/v1/executions/change-status/by-query` - Change status by query

**Execution Recovery**
- `POST /api/v1/executions/restart/by-ids` - Restart executions by IDs
- `POST /api/v1/executions/restart/by-query` - Restart executions by query
- `POST /api/v1/executions/replay/by-ids` - Replay executions by IDs
- `POST /api/v1/executions/replay/by-query` - Replay executions by query

#### Synchronous Execution API

For synchronous execution behavior, use the `wait=true` query parameter[4]:

```bash
curl -X POST 'http://localhost:8080/api/v1/executions/company.team/myflow?wait=true'
```

This makes the API call synchronous and returns all outputs in the response.

**Webhook Execution**
- `GET /api/v1/executions/webhook/{namespace}/{id}/{key}` - Get webhook execution
- `PUT /api/v1/executions/webhook/{namespace}/{id}/{key}` - Update webhook execution  
- `POST /api/v1/executions/webhook/{namespace}/{id}/{key}` - Trigger webhook execution

**Execution Files**
- `GET /api/v1/executions/{executionId}/file` - Get execution file
- `GET /api/v1/executions/{executionId}/file/metas` - Get file metadata
- `GET /api/v1/executions/{executionId}/file/preview` - Preview execution file

### Logs API

The Logs API provides access to execution logs and log management[2].

#### Log Operations

**Get Execution Logs**
- `GET /api/v1/logs/{executionId}` - Get logs for specific execution

**Request Parameters:**
- `executionId` (string, required) - The execution ID
- `minLevel` (enum, optional) - Minimum log level filter (ERROR, WARN, INFO, DEBUG, TRACE)
- `taskRunId` (string, optional) - The task run ID
- `taskId` (string, optional) - The task ID
- `attempt` (int32, optional) - The attempt number

**Response Format:**
```json
[
  {
    "namespace": "string",
    "flowId": "string", 
    "taskId": "string",
    "executionId": "string",
    "taskRunId": "string",
    "attemptNumber": 0,
    "triggerId": "string",
    "timestamp": "1970-01-01T00:00:00.000Z",
    "level": "ERROR",
    "thread": "string",
    "message": "string",
    "deleted": false
  }
]
```

**Log Management**
- `GET /api/v1/logs/search` - Search logs
- `DELETE /api/v1/logs/{executionId}` - Delete execution logs
- `GET /api/v1/logs/{executionId}/download` - Download logs
- `GET /api/v1/logs/{executionId}/follow` - Follow logs (streaming)
- `DELETE /api/v1/logs/{namespace}/{flowId}` - Delete logs by flow

### Plugins API

The Plugins API provides information about available plugins and their configurations[2].

**Plugin Discovery**
- `GET /api/v1/plugins` - List all plugins
- `GET /api/v1/plugins/groups/subgroups` - Get plugin groups and subgroups
- `GET /api/v1/plugins/icons` - Get plugin icons
- `GET /api/v1/plugins/icons/groups` - Get plugin icon groups

**Plugin Information**
- `GET /api/v1/plugins/{cls}` - Get plugin class information
- `GET /api/v1/plugins/{cls}/versions` - Get plugin versions
- `GET /api/v1/plugins/{cls}/versions/{version}` - Get specific plugin version

**Plugin Schemas**
- `GET /api/v1/plugins/schemas/{type}` - Get plugin schema
- `GET /api/v1/plugins/inputs` - Get plugin inputs
- `GET /api/v1/plugins/inputs/{type}` - Get plugin input by type

### Stats API

The Stats API provides execution and system statistics[2].

**Execution Statistics**
- `POST /api/v1/stats/executions/daily` - Daily execution stats
- `POST /api/v1/stats/executions/daily/group-by-flow` - Daily stats grouped by flow
- `POST /api/v1/stats/executions/daily/group-by-namespace` - Daily stats grouped by namespace
- `POST /api/v1/stats/executions/latest/group-by-flow` - Latest stats grouped by flow

**System Statistics**
- `POST /api/v1/stats/logs/daily` - Daily log statistics
- `POST /api/v1/stats/summary` - System summary statistics
- `POST /api/v1/stats/taskruns/daily` - Daily task run statistics

### Misc API

The Misc API provides system configuration and authentication endpoints[2].

**Authentication**
- `POST /api/v1/basicAuth` - Basic authentication
- `POST /api/v1/{tenant}/basicAuth` - Tenant-specific basic authentication

**Configuration**
- `GET /api/v1/configs` - Get system configuration
- `GET /api/v1/{tenant}/configs` - Get tenant configuration

**Usage Information**
- `GET /api/v1/usages/all` - Get all usage information
- `GET /api/v1/{tenant}/usages/all` - Get tenant usage information

### Blueprints API

The Blueprints API manages community templates and blueprints[2].

**Blueprint Operations**
- `GET /api/v1/blueprints/community/{kind}` - Get community blueprints by kind
- `GET /api/v1/blueprints/community/{kind}/{id}` - Get specific blueprint
- `GET /api/v1/blueprints/community/{kind}/{id}/graph` - Get blueprint graph
- `GET /api/v1/blueprints/community/{kind}/{id}/source` - Get blueprint source
- `GET /api/v1/blueprints/community/{kind}/tags` - Get blueprint tags

### Metrics API

The Metrics API provides workflow and task performance metrics[2].

**Execution Metrics**
- `GET /api/v1/metrics/{executionId}` - Get execution metrics
- `GET /api/v1/metrics/aggregates/{namespace}/{flowId}/{metric}` - Get aggregated flow metrics
- `GET /api/v1/metrics/aggregates/{namespace}/{flowId}/{taskId}/{metric}` - Get aggregated task metrics

**Metric Names**
- `GET /api/v1/metrics/names/{namespace}/{flowId}` - Get metric names for flow
- `GET /api/v1/metrics/names/{namespace}/{flowId}/{taskId}` - Get metric names for task
- `GET /api/v1/metrics/tasks/{namespace}/{flowId}` - Get task metrics

### Dashboards API

The Dashboards API manages monitoring dashboards[2].

**Dashboard Management**
- `GET /api/v1/dashboards` - List dashboards
- `POST /api/v1/dashboards` - Create dashboard
- `GET /api/v1/dashboards/{id}` - Get dashboard
- `PUT /api/v1/dashboards/{id}` - Update dashboard
- `DELETE /api/v1/dashboards/{id}` - Delete dashboard

**Dashboard Validation**
- `POST /api/v1/dashboards/validate` - Validate dashboard
- `POST /api/v1/dashboards/validate/chart` - Validate chart
- `POST /api/v1/dashboards/charts/preview` - Preview chart

**Chart Management**
- `POST /api/v1/dashboards/{id}/charts/{chartId}` - Manage dashboard charts

### Namespaces API

The Namespaces API manages namespace-level resources[2].

**Namespace Operations**
- `GET /api/v1/namespaces/search` - Search namespaces
- `GET /api/v1/namespaces/{id}` - Get namespace information

**Secrets Management**
- `GET /api/v1/namespaces/{namespace}/secrets` - Get namespace secrets
- `GET /api/v1/namespaces/{namespace}/inherited-secrets` - Get inherited secrets
- `GET /api/v1/{tenant}/namespaces/{namespace}/secrets` - Get tenant namespace secrets
- `GET /api/v1/{tenant}/namespaces/{namespace}/inherited-secrets` - Get tenant inherited secrets

### Files API

The Files API manages namespace-level file storage[2].

**File Operations**
- `GET /api/v1/namespaces/{namespace}/files` - List files
- `PUT /api/v1/namespaces/{namespace}/files` - Update file
- `POST /api/v1/namespaces/{namespace}/files` - Create file
- `DELETE /api/v1/namespaces/{namespace}/files` - Delete file

**Directory Management**
- `GET /api/v1/namespaces/{namespace}/files/directory` - Get directory contents
- `POST /api/v1/namespaces/{namespace}/files/directory` - Create directory

**File Utilities**
- `GET /api/v1/namespaces/{namespace}/files/export` - Export files
- `GET /api/v1/namespaces/{namespace}/files/search` - Search files
- `GET /api/v1/namespaces/{namespace}/files/stats` - Get file statistics

### Key-Value Store API

The KV API provides key-value storage functionality[2].

**KV Operations**
- `GET /api/v1/namespaces/{namespace}/kv` - List key-value pairs
- `DELETE /api/v1/namespaces/{namespace}/kv` - Delete all key-value pairs
- `GET /api/v1/namespaces/{namespace}/kv/{key}` - Get value by key
- `PUT /api/v1/namespaces/{namespace}/kv/{key}` - Set value by key
- `DELETE /api/v1/namespaces/{namespace}/kv/{key}` - Delete value by key

### Triggers API

The Triggers API manages workflow trigger configurations[2].

**Trigger Management**
- `PUT /api/v1/triggers` - Update triggers
- `GET /api/v1/triggers/search` - Search triggers
- `GET /api/v1/triggers/{namespace}/{flowId}` - Get triggers for flow

**Trigger Control**
- `POST /api/v1/triggers/set-disabled/by-query` - Disable triggers by query
- `POST /api/v1/triggers/set-disabled/by-triggers` - Disable specific triggers
- `POST /api/v1/triggers/unlock/by-query` - Unlock triggers by query
- `POST /api/v1/triggers/unlock/by-triggers` - Unlock specific triggers

**Trigger Operations**
- `POST /api/v1/triggers/{namespace}/{flowId}/{triggerId}/restart` - Restart trigger
- `POST /api/v1/triggers/{namespace}/{flowId}/{triggerId}/unlock` - Unlock trigger

**Backfill Management**
- `POST /api/v1/triggers/backfill/delete` - Delete backfill
- `POST /api/v1/triggers/backfill/delete/by-query` - Delete backfill by query
- `POST /api/v1/triggers/backfill/delete/by-triggers` - Delete backfill by triggers
- `PUT /api/v1/triggers/backfill/pause` - Pause backfill
- `PUT /api/v1/triggers/backfill/unpause` - Unpause backfill

### Task Runs API

The Task Runs API provides access to individual task execution information[2].

**Task Run Operations**
- `GET /api/v1/taskruns/search` - Search task runs

## Usage Examples

### Creating a Flow

```bash
curl -X POST http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  -d "id: created_by_api
namespace: company.team
tasks:
  - id: hello
    type: io.kestra.plugin.core.log.Log
    message: Hello from API"
```

### Executing a Flow

```bash
curl -X POST http://localhost:8080/api/v1/executions/company.team/created_by_api
```

### Executing a Flow with Input

```bash
curl -X POST http://localhost:8080/api/v1/executions/company.team/created_by_api \
  -F "greeting=Hello World"
```

### Managing Key-Value Store

```bash
# Set a value
curl -X PUT http://localhost:8080/api/v1/namespaces/company.team/kv/my_key \
  -d "my_value"

# Get a value
curl -X GET http://localhost:8080/api/v1/namespaces/company.team/kv/my_key

# Delete a value
curl -X DELETE http://localhost:8080/api/v1/namespaces/company.team/kv/my_key
```

### Managing Namespace Files

```bash
# Upload a file
curl -X POST http://localhost:8080/api/v1/namespaces/company.team/files \
  -F "fileContent=@api_example.py" \
  -F "path=api_example.py"

# List files
curl -X GET http://localhost:8080/api/v1/namespaces/company.team/files

# Download a file
curl -X GET http://localhost:8080/api/v1/namespaces/company.team/files?path=api_example.py
```

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

The API does not implement rate limiting in the open-source version, but it's recommended to implement appropriate throttling in production environments.

## API Reference

For interactive API documentation and testing, visit the API reference at your Kestra instance: `http://localhost:8080/docs/api-reference/open-source`[2].

The API follows RESTful conventions and supports both JSON and YAML content types depending on the endpoint. All endpoints are versioned under `/api/v1/` to ensure backward compatibility[5][6].

Fontes
[1] Open Source API https://kestra.io/docs/api-reference/open-source
[2] GET /api/v1/logs/{executionId} - Detailed Example https://kestra.io/docs/api-reference/open-source#get-/api/v1/logs/-executionId-
[3] Extend Kestra with the API https://kestra.io/docs/how-to-guides/api
[4] Cloud & Enterprise Edition API - Kestra https://kestra.io/docs/api-reference/enterprise
[5] Swagger Documentation | Swagger Docs https://swagger.io/docs/
[6] Triggers - Kestra, Open Source Declarative Orchestration Platform https://docs-triggers.kestra-io.pages.dev/docs/workflow-components/triggers
[7] Support Custom Endpoints and LLM Providers · Issue #40 · kestra-io ... https://github.com/kestra-io/plugin-openai/issues/40
[8] Kestra EE API https://kestra.io/docs/enterprise/auth/api
[9] Workflow Automation Using Kestra | Baeldung on Ops https://www.baeldung.com/ops/kestra-workflow-automation
[10] Swagger: API Documentation & Design Tools for Teams https://swagger.io
[11] Kestra, Open Source Declarative Orchestration Platform https://kestra.io
[12] Writing a Data Orchestrator in Java - Foojay.io https://foojay.io/today/writing-a-data-orchestrator-in-java/
[13] API Reference - Kestra https://kestra.io/docs/api-reference
[14] Document Your Plugin - Kestra https://kestra.io/docs/plugin-developer-guide/document
[15] Get Started with the Kestra API | How-to Guide - YouTube https://www.youtube.com/watch?v=uf-b7r_38Zk
[16] kestra/cli/src/main/resources/application.yml at develop - GitHub https://github.com/kestra-io/kestra/blob/develop/cli/src/main/resources/application.yml
[17] Kestra, Open Source Declarative Data Orchestration https://kestra.io/docs
[18] SpecGen Kestra - Gravitee https://www.gravitee.io/blog/specgen-kestra-gravitee
[19] Synchronous Executions API - Kestra https://kestra.io/docs/how-to-guides/synchonous-executions-api
[20] Activity · kestra-io/docs - GitHub https://github.com/kestra-io/kestra.io/activity
[21] Authenticate to the Kestra API with API Tokens - YouTube https://www.youtube.com/watch?v=g-740VZLRdA

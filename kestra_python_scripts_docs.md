# Kestra Python Scripts Documentation

This document provides a comprehensive overview of how to use Python scripts within Kestra, based on the project's existing documentation.

## 🐍 `io.kestra.plugin.scripts.python.Script`

This task allows you to execute an inline Python script.

### Basic Structure

A typical Python script task is defined in your YAML workflow like this:

```yaml
tasks:
  - id: python_script_example
    type: io.kestra.plugin.scripts.python.Script
    description: "An example of an inline Python script."
    script: |
      import os

      print("Hello from a Kestra Python script!")
      
      # Accessing Kestra variables
      webhook_data = os.environ.get('WEBHOOK_DATA')
      if webhook_data:
          print(f"Received data from a webhook: {webhook_data}")

```

### Key Properties

*   `id` (string): A unique identifier for the task.
*   `type` (string): Must be `io.kestra.plugin.scripts.python.Script`.
*   `script` (string): A multi-line string containing the Python code to be executed.
*   `env` (map): A map of environment variables to be passed to the script's execution context. This is the primary way to pass data, like trigger outputs, to your script.

### Passing Data to Scripts

The most common way to pass data to a Python script is via environment variables using the `env` property. You can use Pebble templating to inject dynamic data from triggers, inputs, or other tasks.

**Example with Webhook Trigger Data:**

```yaml
id: python_webhook_processor
namespace: dev.examples

triggers:
  - id: webhook_trigger
    type: io.kestra.plugin.core.trigger.Webhook
    key: "my-secret-key"

tasks:
  - id: process_webhook_with_python
    type: io.kestra.plugin.scripts.python.Script
    env:
      # The entire webhook body is passed as a JSON string
      WEBHOOK_DATA: "{{ trigger.body }}" 
    script: |
      import json
      import os
      
      # Retrieve the data from the environment variable
      data_string = os.environ['WEBHOOK_DATA']
      
      # Parse the JSON string into a Python dictionary
      data = json.loads(data_string)
      
      print(f"Successfully processed webhook data for user: {data.get('user_id')}")

```

### Accessing Kestra Outputs

While not explicitly detailed in the provided context, Kestra typically allows scripts to produce outputs that can be accessed by downstream tasks. This is often done by printing specific formatted strings to standard output, which Kestra's runner then captures and makes available in the `outputs` context variable (e.g., `{{ outputs.task_id.value }}`).

### Best Practices

1.  **Dependency Management**: For complex scripts with external libraries, it is recommended to use a custom Docker image as the runner and install dependencies within the Dockerfile.
2.  **Environment Variables**: Use environment variables (`env`) for passing all external data to your scripts to keep them decoupled and reusable.
3.  **Error Handling**: Implement standard Python `try...except` blocks within your script to handle potential errors gracefully. Kestra will fail the task if the script exits with a non-zero exit code.
4.  **Modularity**: For very long or complex logic, consider breaking it down into smaller scripts or using Subflow tasks to orchestrate multiple script executions. 
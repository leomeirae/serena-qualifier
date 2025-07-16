Plugins/Plugin-Openai/

Chat Completion
Given a prompt, get a response from an LLM using the OpenAI’s Chat
Completions API.
For more information, refer to the Chat Completions API docs.
Examples
Based on a prompt input, generate a completion response and pass it to a
downstream task.
Search Ctrl^ +^ K
Table of Contents
type: "io.kestra.plugin.openai.ChatCompletion" yaml
id: openai_chat
namespace: company.team
inputs:
id: prompt
type: STRING
defaults: What is data orchestration?
tasks:
id: completion
type: io.kestra.plugin.openai.ChatCompletion
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4o
prompt: "{{ inputs.prompt }}"
id: log_output
type: io.kestra.plugin.core.log.Log
yaml
MENU
Send a prompt to OpenAI's ChatCompletion API.
Based on a prompt input, ask OpenAI to call a function that determines whether
you need to respond to a customer's review immediately or wait until later, and
then comes up with a suggested response.
message: "{{ outputs.completion.choices[0].message.content }}"
id: openai_chat
namespace: company.team
tasks:
id: prompt
type: io.kestra.plugin.openai.ChatCompletion
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4o
prompt: Explain in one sentence why data engineers build data
pipelines
id: use_output
type: io.kestra.plugin.core.log.Log
message: "{{ outputs.prompt.choices | jq('.[].message.content') |
first }}"
yaml
id: openai_chat
namespace: company.team
inputs:
id: prompt
type: STRING
defaults: I love your product and would purchase it again!
tasks:
id: prioritize_response
type: io.kestra.plugin.openai.ChatCompletion
apiKey: "yourOpenAIapiKey"
model: gpt-4o
messages:
yaml
Properties
apiKey * string
OpenAI API key

model * string
role: user
content: "{{ inputs.prompt }}"
functions:
name: respond_to_review
description: Given the customer product review provided as input,
determines how urgently a reply is required and then provides suggested
response text.
parameters:
name: response_urgency
type: string
description: How urgently this customer review needs a reply.
Bad reviews
must be addressed immediately before anyone sees
them. Good reviews can
wait until later.
required: true
enumValues:
reply_immediately
reply_later
name: response_text
type: string
description: The text to post online in response to this
review.
required: true
id: response_urgency
type: io.kestra.plugin.core.debug.Return
format: "{{
outputs.prioritize_response.choices[0].message.function_call.arguments.res
ponse_urgency }}"
id: response_text
type: io.kestra.plugin.core.debug.Return
format: "{{
outputs.prioritize_response.choices[0].message.function_call.arguments.res
ponse_text }}"
ID of the model to use e.g. 'gpt-4'

See the OpenAI model's documentation page for more details.

clientTimeout integer
Default 10

The maximum number of seconds to wait for a response

frequencyPenalty number string
Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing

frequency in the text so far. Defaults to 0.

functionCall string
The name of the function OpenAI should generate a call for.

Enter a specific function name, or 'auto' to let the model decide. The default is auto.

functions array
SubType ChatCompletion-PluginChatFunction

The function call(s) the API can use when generating completions.

logitBias object
SubType integer

Modify the likelihood of specified tokens appearing in the completion. Defaults to null.

maxTokens integer string
The maximum number of tokens to generate in the chat completion. No limits are set by default.

messages array
SubType ChatMessage

A list of messages comprising the conversation so far

This property is required if prompt is not set.

n integer string
How many chat completion choices to generate for each input message. Defaults to 1.

presencePenalty number string
Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear

in the text so far. Defaults to 0.

prompt string
The prompt(s) to generate completions for. By default, this prompt will be sent as a user role.

If not provided, make sure to set the messages property.

stop array
SubType string

Up to 4 sequences where the API will stop generating further tokens. Defaults to null.

temperature number string
What sampling temperature to use, between 0 and 2. Defaults to 1.

topP number string
An alternative to sampling with temperature, where the model considers the results of the tokens

with top_p probability mass. Defaults to 1.

user string
A unique identifier representing your end-user

Outputs
choices array
SubType ChatCompletionChoice

A list of all generated completions

id string
Unique ID assigned to this Chat Completion

model string
The GPT model used

object string
The type of object returned, should be "chat.completion".

usage Usage
The API usage for this request

Definitions
com.theokanning.openai.completion.chat.ChatFunctionCall
arguments JsonNode
name string
io.kestra.plugin.openai.ChatCompletion-PluginChatFunctionParameter
description * string
A description of the function parameter

Provide as many details as possible to ensure the model returns an accurate parameter.

name * string
The name of the function parameter

type * string
The OpenAPI data type of the parameter

Valid types are string, number, integer, boolean, array, object

enumValues array
SubType string

A list of values that the model must choose from when setting this parameter.
Optional, but useful when for classification problems.

required boolean string
Whether or not the model is required to provide this parameter

Defaults to false.

com.fasterxml.jackson.databind.JsonNode
io.kestra.plugin.openai.ChatCompletion-PluginChatFunction
description string
A description of what the function does

name string
The name of the function

parameters array
SubType ChatCompletion-PluginChatFunctionParameter

The function's parameters

com.theokanning.openai.completion.chat.ChatCompletionChoice
finish_reason string
index integer
message ChatMessage
com.theokanning.openai.Usage
completion_tokens integer
prompt_tokens integer
total_tokens integer
com.theokanning.openai.completion.chat.ChatMessage
content string
function_call ChatFunctionCall
name string
role string




Plugins/Plugin-Openai/

Responses
Interact with LLMs using OpenAI's Responses API with built-in tools and
structured output.
For more information, refer to the OpenAI Responses API docs.
Examples
Send a simple text prompt to OpenAI and output the result as text.
Search Ctrl^ +^ K
Table of Contents
type: "io.kestra.plugin.openai.Responses" yaml
id: simple_text
namespace: company.team
inputs:
id: prompt
type: STRING
defaults: Explain what is Kestra in 3 sentences
tasks:
id: explain
type: io.kestra.plugin.openai.Responses
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4.1-mini
input: "{{ inputs.prompt }}"
id: log
type: io.kestra.plugin.core.log.Log
message: "{{ outputs.explain.outputText }}"
yaml
MENU
Use the OpenAI's web-search tool to find recent trends in workflow
orchestration.
Use the OpenAI's web-search tool to get a daily summary of local news via email.
id: web_search
namespace: company.team
inputs:
id: prompt
type: STRING
defaults: List recent trends in workflow orchestration
tasks:
id: trends
type: io.kestra.plugin.openai.Responses
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4.1-mini
input: "{{ inputs.prompt }}"
toolChoice: REQUIRED
tools:
- type: web_search_preview
id: log
type: io.kestra.plugin.core.log.Log
message: "{{ outputs.trends.outputText }}"
yaml
id: fetch_local_news
namespace: company.team
inputs:
id: prompt
type: STRING
defaults: Summarize top 5 news from my region
tasks:
id: news
type: io.kestra.plugin.openai.Responses
yaml
Use the OpenAI's function-calling tool to respond to a customer review and
determine urgency of response.
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4.1-mini
input: "{{ inputs.prompt }}"
toolChoice: REQUIRED
tools:
type: web_search_preview
search_context_size: low # optional; low, medium, high
user_location:
type: approximate # OpenAI doesn't provide other types atm, and
it cannot be omitted
city: Berlin
region: Berlin
country: DE
id: mail
type: io.kestra.plugin.notifications.mail.MailSend
from: your_email
to: your_email
username: your_email
host: mail.privateemail.com
port: 465
password: "{{ secret('EMAIL_PASSWORD') }}"
sessionTimeout: 6000
subject: Daily News Summary
htmlTextContent: "{{ outputs.news.outputText }}"
triggers:
id: schedule
type: io.kestra.plugin.core.trigger.Schedule
cron: "0 9 * * *"
id: responses_functions
namespace: company.team
inputs:
id: prompt
type: STRING
defaults: I love your product and would purchase it again!
tasks:
id: openai
yaml
Run a stateful chat with OpenAI using the Responses API.
type: io.kestra.plugin.openai.Responses
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4.1-mini
input: "{{ inputs.prompt }}"
toolChoice: AUTO
tools:
type: function
name: respond_to_review
description: >-
Given the customer product review provided as input, determine
how
urgently a reply is required and then provide suggested response
text.
strict: true
parameters:
type: object
required:
response_urgency
response_text
properties:
response_urgency:
type: string
description: >-
How urgently this customer review needs a reply. Bad
reviews must
be addressed immediately before anyone sees them. Good
reviews
can wait until later.
enum:
reply_immediately
reply_later
response_text:
type: string
description: The text to post online in response to this
review.
additionalProperties: false
id: output
type: io.kestra.plugin.core.output.OutputValues
values:
urgency: "{{ fromJson(outputs.openai.outputText).response_urgency
}}"
response: "{{ fromJson(outputs.openai.outputText).response_text }}"
Return a structured output with nutritional information about a food item using
OpenAI's Responses API.
id: stateful_chat
namespace: company.team
inputs:
id: user_input
type: STRING
defaults: How can I get started with Kestra as a microservice
developer?
id: reset_conversation
type: BOOL
defaults: false
tasks:
id: maybe_reset_conversation
runIf: "{{ inputs.reset_conversation }}"
type: io.kestra.plugin.core.kv.Delete
key: "RESPONSE_ID"
id: chat_request
type: io.kestra.plugin.openai.Responses
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4.
previousResponseId: "{{ kv('RESPONSE_ID', errorOnMissing=false) }}"
input:
- role: user
content:
- type: input_text
text: "{{ inputs.user_input }}"
id: store_response
type: io.kestra.plugin.core.kv.Set
key: "RESPONSE_ID"
value: "{{ outputs.chat_request.responseId }}"
id: output_log
type: io.kestra.plugin.core.log.Log
message: "Response: {{ outputs.chat_request.outputText }}"
yaml
id: structured_output_demo yaml
namespace: company.team

inputs:

id: food
type: STRING
defaults: Avocado
tasks:

id: generate_structured_response
type: io.kestra.plugin.openai.Responses
apiKey: "{{ secret('OPENAI_API_KEY') }}"
model: gpt-4.1-mini
input: "Fill in nutrients information for the following food: {{
inputs.food }}"
text:
format:
type: json_schema
name: food_macronutrients
schema:
type: object
properties:
food:
type: string
description: The name of the food or meal.
macronutrients:
type: object
description: Macro-nutritional content of the food.
properties:
carbohydrates:
type: number
description: Amount of carbohydrates in grams.
proteins:
type: number
description: Amount of proteins in grams.
fats:
type: number
description: Amount of fats in grams.
required:
carbohydrates
proteins
fats
additionalProperties: false
vitamins:
type: object
description: Specific vitamins present in the food.
properties:
vitamin_a:
type: number
description: Amount of Vitamin A in micrograms.
vitamin_c:
Properties
apiKey * string
OpenAI API key

input * object
Input to the prompt's context window

model * string
Model name to use (e.g., gpt-4o)

See the OpenAI model's documentation

clientTimeout integer
type: number
description: Amount of Vitamin C in milligrams.
vitamin_d:
type: number
description: Amount of Vitamin D in micrograms.
vitamin_e:
type: number
description: Amount of Vitamin E in milligrams.
vitamin_k:
type: number
description: Amount of Vitamin K in micrograms.
required:
vitamin_a
vitamin_c
vitamin_d
vitamin_e
vitamin_k
additionalProperties: false
required:
food
Default^10

The maximum number of seconds to wait for a response

maxOutputTokens integer string
Maximum tokens in the response

parallelToolCalls boolean string
Allow parallel tool execution

previousResponseId string
ID of previous response to continue conversation

reasoning object
SubType string

Reasoning configuration

Configuration for model reasoning process

store boolean string
Default true

Whether to persist response and chat history

If true (default), persists in OpenAI's storage

temperature number string
Default 1.

Sampling temperature (0-2)

text object
Text response configuration

Configure the format of the model's text response

toolChoice string
Possible Values NONE AUTO REQUIRED

Controls which tool is called by the model

none: no tools, auto: model picks, required: must use tools

tools array
SubType Tool

List of built-in tools to enable

e.g., web_search, file_search, function calling

topP number string
Default 1.

Nucleus sampling parameter (0-1)

user string
A unique identifier representing your end-user

Outputs
outputText string
The generated text output

rawResponse object
Full API response for advanced use

responseId string
ID of the persisted response

sources array
SubType string

List of sources (for web/file search)

Definitions
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.models.responses.Tool-CodeInterpreter
container JsonField
type JsonValue
com.openai.models.responses.WebSearchTool
type JsonField
com.openai.core.JsonField
com.openai.core.JsonValue
com.openai.models.responses.ComputerTool
environment JsonField
type JsonValue
com.openai.models.responses.Tool
codeInterpreter Tool-CodeInterpreter
computerUsePreview ComputerTool
fileSearch FileSearchTool
function FunctionTool
imageGeneration Tool-ImageGeneration
localShell JsonValue
mcp Tool-Mcp
webSearch WebSearchTool
com.openai.core.JsonField
com.openai.models.responses.Tool-Mcp
headers JsonField
type JsonValue
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.models.responses.FileSearchTool
filters JsonField
type JsonValue
com.openai.models.responses.FunctionTool
description JsonField
name JsonField
parameters JsonField
strict JsonField
type JsonValue
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.core.JsonField
com.openai.models.responses.Tool-ImageGeneration
background JsonField
model JsonField
moderation JsonField
quality JsonField
size JsonField
type JsonValue
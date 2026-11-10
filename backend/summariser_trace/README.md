# Terraform summariser request trace

This is a live trace of `summarize_for_sdg` for
[hashicorp/terraform](https://github.com/hashicorp/terraform). It records the
input acquisition, preprocessing, outbound Groq POST, HTTP response, parsed
content, and value returned by the function.

The request was sent using the configured `GROQ_API_KEY`. The credential is
intentionally redacted everywhere in this report. Groq's private `reasoning`
response field is also omitted; the user-facing `message.content`, status,
request IDs, and usage fields are preserved.

## Result at a glance

- **Groq HTTP status:** `200`
- **Model:** `openai/gpt-oss-20b`
- **Groq request ID:** `req_01m52wjsgbez28dq48e5r64qas`
- **Model finish reason:** `stop`
- **Parsed model content:** `NO_SDG_SIGNAL`
- **Final `summarize_for_sdg` return value:** `NO_SDG_SIGNAL`

This result follows the configured prompt: Terraform is general-purpose
infrastructure tooling, and the README/metadata do not identify a specific
population, social problem, or domain impact. The prompt explicitly says not to
infer relevance just because general-purpose tooling could be used in many
sectors.

## Stage 1: Acquire repository data

The trace was captured at `2026-10-16T17:36:26.882748+00:00`. During that run,
it fetched the public repository metadata and README:

| Data | Source | HTTP | Result |
|---|---|---:|---|
| Repository metadata and topics | `https://api.github.com/repos/hashicorp/terraform` | 200 | `hashicorp/terraform` |
| README | `https://raw.githubusercontent.com/hashicorp/terraform/main/README.md` | 200 | 3,935 characters |

The metadata provided:

- **Name:** `terraform`
- **Description:** `Terraform enables you to safely and predictably create, change, and improve infrastructure. It is a source-available tool that codifies APIs into declarative configuration files that can be shared amongst team members, treated as code, edited, reviewed, and versioned.`
- **Topics:** `cloud`, `cloud-management`, `graph`, `infrastructure-as-code`, `terraform`

## Stage 2: Prepare input for the summariser

The function received the repository README, name, description, and topics
above. `_prepare_for_llm` cleaned the README and passed 2,834 characters to the
prompt. The configured maximum is 12,000 characters, so this input was not
truncated by that limit.

The exact user message supplied in the POST was:

```text
PROJECT NAME: terraform
PROJECT DESCRIPTION (from repository metadata): Terraform enables you to safely and predictably create, change, and improve infrastructure. It is a source-available tool that codifies APIs into declarative configuration files that can be shared amongst team members, treated as code, edited, reviewed, and versioned.
TOPICS/TAGS: cloud, cloud-management, graph, infrastructure-as-code, terraform

README CONTENT:
# Terraform

- Website: 
- Forums: HashiCorp Discuss
- Documentation: 
- Tutorials: HashiCorp's Learn Platform
- Certification Exam: HashiCorp Certified: Terraform Associate

Terraform is a tool for building, changing, and versioning infrastructure safely and efficiently. Terraform can manage existing and popular service providers as well as custom in-house solutions.

The key features of Terraform are:

- **Infrastructure as Code**: Infrastructure is described using a high-level configuration syntax. This allows a blueprint of your datacenter to be versioned and treated as you would any other code. Additionally, infrastructure can be shared and re-used.

- **Execution Plans**: Terraform has a "planning" step where it generates an execution plan. The execution plan shows what Terraform will do when you call apply. This lets you avoid any surprises when Terraform manipulates infrastructure.

- **Resource Graph**: Terraform builds a graph of all your resources, and parallelizes the creation and modification of any non-dependent resources. Because of this, Terraform builds infrastructure as efficiently as possible, and operators get insight into dependencies in their infrastructure.

- **Change Automation**: Complex changesets can be applied to your infrastructure with minimal human interaction. With the previously mentioned execution plan and resource graph, you know exactly what Terraform will change and in what order, avoiding many possible human errors.

For more information, refer to the What is Terraform? page on the Terraform website.

## Getting Started & Documentation

Documentation is available on the Terraform website:

- Introduction
- Documentation

If you're new to Terraform and want to get started creating infrastructure, please check out our Getting Started guides on HashiCorp's learning platform. There are also additional guides to continue your learning.

Show off your Terraform knowledge by passing a certification exam. Visit the certification page for information about exams and find study materials on HashiCorp's learning platform.

## Developing Terraform

This repository contains only Terraform core, which includes the command line interface and the main graph engine. Providers are implemented as plugins, and Terraform can automatically download providers that are published on the Terraform Registry. HashiCorp develops some providers, and others are developed by other organizations. For more information, refer to Plugin development.

- To learn more about compiling Terraform and contributing suggested changes, refer to the contributing guide.

- To learn more about how we handle bug reports, refer to the bug triage guide.

- To learn how to contribute to the Terraform documentation, refer to the Web Unified Docs repository.

## License

Business Source License 1.1

Write the SDG-classification paragraph now.
```

The exact system prompt is `SYSTEM_PROMPT` in
[the summariser implementation](../services/summariser.py). At capture time it
was 3,856 characters; its SHA-256 was
`d282a0cbf9130e27e582ab6a9fc83febce1d5a9dc76325d5028e996b8c5ad529`. This
identifies the exact prompt used without duplicating it here.

## Stage 3: Outbound HTTP request

The summariser made one POST to
`https://api.groq.com/openai/v1/chat/completions`.

Request headers (credential value redacted):

```text
Authorization: [REDACTED]
Content-Type: application/json
```

Request body structure (the exact user message is reproduced in Stage 2; the
system message is the `SYSTEM_PROMPT` identified by the SHA-256 above):

```json
{
  "model": "openai/gpt-oss-20b",
  "temperature": 0.1,
  "max_tokens": 600,
  "reasoning_effort": "low",
  "messages": [
    {
      "role": "system",
      "content": "SYSTEM_PROMPT from backend/services/summariser.py (3,856 characters; SHA-256 recorded above)"
    },
    {
      "role": "user",
      "content": "Exact 3,316-character user message shown in Stage 2"
    }
  ]
}
```

The function's request timeout was 60 seconds. The bearer credential is not
included in this report.

## Stage 4: HTTP response from Groq

Groq returned HTTP `200` with `Content-Type: application/json` and
`x-request-id: req_01m52wjsgbez28dq48e5r64qas`.

Response body, with only the private `message.reasoning` value omitted:

```json
{
  "id": "chatcmpl-9bbe7e9d-ec9b-4013-9a18-6398f18e6fb9",
  "object": "chat.completion",
  "created": 1792172189,
  "model": "openai/gpt-oss-20b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "NO_SDG_SIGNAL",
        "reasoning": "<OMITTED: private model reasoning>"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "queue_time": 0.38227962,
    "prompt_tokens": 1494,
    "prompt_time": 0.078784626,
    "completion_tokens": 42,
    "completion_time": 0.04254152,
    "total_tokens": 1536,
    "total_time": 0.121326146,
    "completion_tokens_details": {
      "reasoning_tokens": 29
    }
  },
  "usage_breakdown": null,
  "system_fingerprint": "fp_ed70b23331",
  "x_groq": {
    "id": "req_01m52wjsgbez28dq48e5r64qas",
    "seed": 420195029
  },
  "service_tier": "on_demand"
}
```

## Stage 5: Parse, validate, and return

1. `response.json()` parsed the HTTP response body.
2. The summariser selected `choices[0].message.content`, which was
   `NO_SDG_SIGNAL`.
3. `_validate_output` recognizes that exact sentinel and returns it unchanged.
4. `summarize_for_sdg` returned **`NO_SDG_SIGNAL`** to its caller. It did not
   return a fallback summary.

## Earlier preliminary live call

Before retrieving the GitHub topics, an exploratory POST was also made with
the same repository README and description, but with manually supplied topics
`infrastructure-as-code`, `terraform`, and `cloud`. That request returned HTTP
`200`, `NO_SDG_SIGNAL`, and Groq request ID
`req_01m52whk0de26t93p8zwr73b3q`. The detailed trace above is the final run
using the topics fetched from GitHub.

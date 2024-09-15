# Support Bot

This demos a complete example and aims for an AWS Lex- or Cognigy-like experience.

## Run the example

1. Install additional dependencies:
   ```shell
    $ pip install 'litellm[proxy]'
    $ pip install aiosmtpd
    ```
2. Start the LiteLLM Proxy Server (LLM Gateway):
   ```shell
   $ litellm --detailed_debug --config ./litellm_config.yml
   ```
3. Start the SMTP server:
   ```shell
   $ aiosmtpd -n
   ```
4. Start the NeMo Guardrails chat:
   ```shell
   $ python -m nemoguardrails.__main__ chat --streaming --config .
   ```

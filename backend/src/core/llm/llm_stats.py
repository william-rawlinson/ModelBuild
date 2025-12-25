class LLMStats:

    """
    Class to track LLM stats (token usage, cost etc.) across the workflow
    """

    def __init__(self):
        self.output_tokens = {
            "gpt-4o-2024-11-20": 0,
            "gpt-4-turbo-2024-04-09": 0,
            "claude-3-5-sonnet-20241022": 0,
            "o1-2024-12-17": 0,
            'claude-opus-4-20250514': 0,
            'claude-sonnet-4-20250514': 0,
            'claude-3-7-sonnet-latest': 0,
            'o3-2025-04-16': 0,
            'o3-mini-2025-01-31': 0,
            'gpt-4.1-2025-04-14': 0,
            'gpt-4-0613': 0,
            'gpt-3.5-turbo-0125': 0,
            "bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0": 0,
            "bedrock:anthropic.claude-3-7-sonnet-20250219-v1:0":0,
            'bedrock:anthropic.claude-3-5-sonnet-20240620-v1:0':0,
        }
        self.input_tokens = {key: 0 for key in self.output_tokens}
        self.number_calls = {key: 0 for key in self.output_tokens}
        self.total_cost = 0.00

    def update(self, response, model):
        if model in self.number_calls:
            self.number_calls[model] += 1
            # Handle OpenAI models
            if model.startswith('gpt') or model.startswith('o'):
                self.output_tokens[model] += response.usage.completion_tokens
                self.input_tokens[model] += response.usage.prompt_tokens
            # Handle Claude models
            elif model.startswith('claude'):
                self.output_tokens[model] += response.usage.output_tokens
                self.input_tokens[model] += response.usage.input_tokens
            elif model.startswith('bedrock'):
                self.output_tokens[model] += response["usage"]["output_tokens"]
                self.input_tokens[model] += response["usage"]["input_tokens"]

    def get_total_cost(self):
        cost_per_token = {
            "gpt-4o-2024-11-20": {"input": 2.5/1000000, "output": 10/1000000},
            "gpt-4-turbo-2024-04-09": {"input": 10/1000000, "output": 30/1000000},
            "claude-3-5-sonnet-20241022": {"input": 3/1000000, "output": 15/1000000},
            "claude-opus-4-20250514": {"input": 15/1000000, "output": 75/1000000},
            "claude-sonnet-4-20250514": {"input": 3/1000000, "output": 15/1000000},
            "claude-3-7-sonnet-latest": {"input": 3/1000000, "output": 15/1000000},
            "o1-2024-12-17": {"input": 15/1000000, "output": 60/1000000},
            "o3-2025-04-16": {"input": 2/1000000, "output": 8/1000000},
            "o3-mini-2025-01-31": {"input": 1.1/1000000, "output": 4.4/1000000},
            "gpt-4.1-2025-04-14": {"input": 2/1000000, "output": 8/1000000},
            "gpt-4-0613": {"input": 30/1000000, "output": 60/1000000},
            "gpt-3.5-turbo-0125": {"input": 0.5/1000000, "output": 1.5/1000000},
            "bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 3/1000000, "output": 15/1000000},
            "bedrock:anthropic.claude-3-7-sonnet-20250219-v1:0": {"input": 3/1000000, "output": 15/1000000},
            'bedrock:anthropic.claude-3-5-sonnet-20240620-v1:0': {"input": 3/1000000, "output": 15/1000000},
        }
        total_cost = 0
        for model, costs in cost_per_token.items():
            total_cost += self.output_tokens[model] * costs["output"]
            total_cost += self.input_tokens[model] * costs["input"]
        return total_cost

    def get_output_tokens(self):
        result = "; ".join(
            f"{model}: {tokens:,}" for model, tokens in self.output_tokens.items() if tokens > 0
        )
        return f"[{result}]" if result else "[None]"

    def get_input_tokens(self):
        result = "; ".join(
            f"{model}: {tokens:,}" for model, tokens in self.input_tokens.items() if tokens > 0
        )
        return f"[{result}]" if result else "[None]"

    def get_number_calls(self):
        result = "; ".join(
            f"{model}: {calls:,}" for model, calls in self.number_calls.items() if calls > 0
        )
        return f"[{result}]" if result else "[None]"

    def get_stats(self):
        total_cost = self.get_total_cost()
        output_tokens = self.get_output_tokens()
        input_tokens = self.get_input_tokens()
        number_calls = self.get_number_calls()
        return (f"""Calls made - {number_calls}.
Total cost -    ${total_cost}.
Input tokens -    {input_tokens}.
Output tokens -    {output_tokens}.""")

    def reset(self):
        self.__init__()
# -*- coding: utf-8 -*-
"""LiteLLM_AB_TestLLMs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y7zcpuJT5rqJYEELeg9UfP1Zf8gFVR_o

# LiteLLM A/B Testing LLMs in production

* LiteLLM allows you to use 100+ LLMs as a drop in replacement for `gpt-3.5-turbo`

This tutorial walks through how to use LiteLLM to easily A/B Test LLMs in production

# Example 1: A/B Test GPT-4 & GPT-3.5

# Step 1
👉 Get your `id` from here: https://admin.litellm.ai/
"""

from litellm import completion_with_split_tests
import os

## set ENV variables
os.environ["OPENAI_API_KEY"] = "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"


# define a dict of model id and % of requests for model
# see models here: https://docs.litellm.ai/docs/completion/supported
split_per_model = {
	"gpt-4": 0.3,
	"gpt-3.5-turbo": 0.7
}

messages = [{ "content": "Hello, how are you?","role": "user"}]

completion_with_split_tests(messages=messages, use_client=True,
   id="91fad14a-8c0f-4e99-8eaa-68245435aa80") # enter your id

"""## A/B Test GPT-4 and Claude-2"""

from litellm import completion_with_split_tests
import os

## set ENV variables
os.environ["ANTHROPIC_API_KEY"] = ""

# define a dict of model id and % of requests for model
split_per_model = {
	"gpt-4": 0.3,
	"claude-2": 0.7
}

messages = [{ "content": "Hello, how are you?","role": "user"}]


completion_with_split_tests(messages=messages, use_client=True,
   id="91fad14a-8c0f-4e99-8eaa-68245435aa80") # enter your id
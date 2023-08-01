import os, openai, cohere, replicate, sys
from typing import Any
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import traceback
import dotenv
import traceback
import litellm
from litellm import client, logging, exception_type, timeout, success_callback, failure_callback
import random
####### ENVIRONMENT VARIABLES ###################
dotenv.load_dotenv() # Loading env variables using dotenv



def get_optional_params(
    # 12 optional params
    functions = [],
    function_call = "",
    temperature = 1,
    top_p = 1,
    n = 1,
    stream = False,
    stop = None,
    max_tokens = float('inf'),
    presence_penalty = 0,
    frequency_penalty = 0,
    logit_bias = {},
    user = "",
):
  optional_params = {}
  if functions != []:
      optional_params["functions"] = functions
  if function_call != "":
      optional_params["function_call"] = function_call
  if temperature != 1:
      optional_params["temperature"] = temperature
  if top_p != 1:
      optional_params["top_p"] = top_p
  if n != 1:
      optional_params["n"] = n
  if stream:
      optional_params["stream"] = stream
  if stop != None:
      optional_params["stop"] = stop
  if max_tokens != float('inf'):
      optional_params["max_tokens"] = max_tokens
  if presence_penalty != 0:
      optional_params["presence_penalty"] = presence_penalty
  if frequency_penalty != 0:
      optional_params["frequency_penalty"] = frequency_penalty
  if logit_bias != {}:
      optional_params["logit_bias"] = logit_bias
  if user != "":
      optional_params["user"] = user
  return optional_params

####### COMPLETION ENDPOINTS ################
#############################################
@client
@timeout(60) ## set timeouts, in case calls hang (e.g. Azure) - default is 60s, override with `force_timeout`
def completion(
    model, messages, # required params
    # Optional OpenAI params: see https://platform.openai.com/docs/api-reference/chat/create
    functions=[], function_call="", # optional params
    temperature=1, top_p=1, n=1, stream=False, stop=None, max_tokens=float('inf'),
    presence_penalty=0, frequency_penalty=0, logit_bias={}, user="",
    # Optional liteLLM function params
    *, force_timeout=60, azure=False, logger_fn=None, verbose=False
  ):
  try:
    # check if user passed in any of the OpenAI optional params
    optional_params = get_optional_params(
      functions=functions, function_call=function_call, 
      temperature=temperature, top_p=top_p, n=n, stream=stream, stop=stop, max_tokens=max_tokens,
      presence_penalty=presence_penalty, frequency_penalty=frequency_penalty, logit_bias=logit_bias, user=user
    )
    if azure == True:
      # azure configs
      openai.api_type = "azure"
      openai.api_base = os.environ.get("AZURE_API_BASE")
      openai.api_version = os.environ.get("AZURE_API_VERSION")
      openai.api_key = os.environ.get("AZURE_API_KEY")
      ## LOGGING
      logging(model=model, input=messages, azure=azure, logger_fn=logger_fn)
      ## COMPLETION CALL
      response = openai.ChatCompletion.create(
        engine=model,
        messages = messages,
        **optional_params
      )
    elif model in litellm.open_ai_chat_completion_models:
      openai.api_type = "openai"
      openai.api_base = "https://api.openai.com/v1"
      openai.api_version = None
      openai.api_key = os.environ.get("OPENAI_API_KEY")
      ## LOGGING
      logging(model=model, input=messages, azure=azure, logger_fn=logger_fn)

      ## COMPLETION CALL
      response = openai.ChatCompletion.create(
        model=model,
        messages = messages,
        **optional_params
      )
    elif model in litellm.open_ai_text_completion_models:
      openai.api_type = "openai"
      openai.api_base = "https://api.openai.com/v1"
      openai.api_version = None
      openai.api_key = os.environ.get("OPENAI_API_KEY")
      prompt = " ".join([message["content"] for message in messages])
      ## LOGGING
      logging(model=model, input=prompt, azure=azure, logger_fn=logger_fn)
      ## COMPLETION CALL
      response = openai.Completion.create(
          model=model,
          prompt = prompt
      )
    elif "replicate" in model:
      # replicate defaults to os.environ.get("REPLICATE_API_TOKEN")
      # checking in case user set it to REPLICATE_API_KEY instead 
      if not os.environ.get("REPLICATE_API_TOKEN") and os.environ.get("REPLICATE_API_KEY"):
        replicate_api_token = os.environ.get("REPLICATE_API_KEY")
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
      prompt = " ".join([message["content"] for message in messages])
      input = {"prompt": prompt}
      if max_tokens != float('inf'):
        input["max_length"] = max_tokens # for t5 models 
        input["max_new_tokens"] = max_tokens # for llama2 models 
      ## LOGGING
      logging(model=model, input=input, azure=azure, additional_args={"max_tokens": max_tokens}, logger_fn=logger_fn)
      ## COMPLETION CALL
      output = replicate.run(
        model,
        input=input)
      response = ""
      for item in output: 
        response += item
      new_response = {
        "choices": [
          {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": response,
                "role": "assistant"
            }
          }
        ]
      }
      response = new_response
    elif model in litellm.anthropic_models:
      #anthropic defaults to os.environ.get("ANTHROPIC_API_KEY")
      prompt = f"{HUMAN_PROMPT}" 
      for message in messages:
        if "role" in message:
          if message["role"] == "user":
            prompt += f"{HUMAN_PROMPT}{message['content']}"
          else:
            prompt += f"{AI_PROMPT}{message['content']}"
        else:
          prompt += f"{HUMAN_PROMPT}{message['content']}"
      prompt += f"{AI_PROMPT}"
      anthropic = Anthropic()
      # check if user passed in max_tokens != float('inf')
      if max_tokens != float('inf'):
        max_tokens_to_sample = max_tokens
      else:
        max_tokens_to_sample = 300 # default in Anthropic docs https://docs.anthropic.com/claude/reference/client-libraries
      ## LOGGING
      logging(model=model, input=prompt, azure=azure, additional_args={"max_tokens": max_tokens}, logger_fn=logger_fn)
      ## COMPLETION CALL
      completion = anthropic.completions.create(
          model=model,
          prompt=prompt,
          max_tokens_to_sample=max_tokens_to_sample
      )
      new_response = {
        "choices": [
          {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": completion.completion,
                "role": "assistant"
            }
          }
        ]
      }
      print_verbose(f"new response: {new_response}")
      response = new_response
    elif model in litellm.cohere_models:
      cohere_key = os.environ.get("COHERE_API_KEY")
      co = cohere.Client(cohere_key)
      prompt = " ".join([message["content"] for message in messages])
      ## LOGGING
      logging(model=model, input=prompt, azure=azure, logger_fn=logger_fn)
      ## COMPLETION CALL
      response = co.generate(  
        model=model,
        prompt = prompt
      )
      new_response = {
          "choices": [
              {
                  "finish_reason": "stop",
                  "index": 0,
                  "message": {
                      "content": response[0].text,
                      "role": "assistant"
                  }
              }
          ],
      }
      response = new_response

    elif model in litellm.open_ai_chat_completion_models:
      openai.api_type = "openai"
      openai.api_base = "https://api.openai.com/v1"
      openai.api_version = None
      openai.api_key = os.environ.get("OPENAI_API_KEY")
      ## LOGGING
      logging(model=model, input=messages, azure=azure, logger_fn=logger_fn)
      ## COMPLETION CALL
      response = openai.ChatCompletion.create(
          model=model,
          messages = messages
      )
    elif model in litellm.open_ai_text_completion_models:
      openai.api_type = "openai"
      openai.api_base = "https://api.openai.com/v1"
      openai.api_version = None
      openai.api_key = os.environ.get("OPENAI_API_KEY")
      prompt = " ".join([message["content"] for message in messages])
      ## LOGGING
      logging(model=model, input=prompt, azure=azure, logger_fn=logger_fn)
      ## COMPLETION CALL
      response = openai.Completion.create(
          model=model,
          prompt = prompt
      )
    else: 
      logging(model=model, input=messages, azure=azure, logger_fn=logger_fn)
      args = locals()
      raise ValueError(f"No valid completion model args passed in - {args}")
    return response
  except Exception as e:
    # log the original exception
    logging(model=model, input=messages, azure=azure, additional_args={"max_tokens": max_tokens}, logger_fn=logger_fn, exception=e)
    ## Map to OpenAI Exception
    raise exception_type(model=model, original_exception=e)


### EMBEDDING ENDPOINTS ####################
@client
@timeout(60) ## set timeouts, in case calls hang (e.g. Azure) - default is 60s, override with `force_timeout`
def embedding(model, input=[], azure=False, force_timeout=60, logger_fn=None):
  response = None
  if azure == True:
    # azure configs
    openai.api_type = "azure"
    openai.api_base = os.environ.get("AZURE_API_BASE")
    openai.api_version = os.environ.get("AZURE_API_VERSION")
    openai.api_key = os.environ.get("AZURE_API_KEY")
    ## LOGGING
    logging(model=model, input=input, azure=azure, logger_fn=logger_fn)
    ## EMBEDDING CALL
    response = openai.Embedding.create(input=input, engine=model)
    print_verbose(f"response_value: {str(response)[:50]}")
  elif model in litellm.open_ai_embedding_models:
    openai.api_type = "openai"
    openai.api_base = "https://api.openai.com/v1"
    openai.api_version = None
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    ## LOGGING
    logging(model=model, input=input, azure=azure, logger_fn=logger_fn)
    ## EMBEDDING CALL
    response = openai.Embedding.create(input=input, model=model)
    print_verbose(f"response_value: {str(response)[:50]}")
  else: 
    logging(model=model, input=input, azure=azure, logger_fn=logger_fn)
    args = locals()
    raise ValueError(f"No valid embedding model args passed in - {args}")
  
  return response

####### HELPER FUNCTIONS ################
## Set verbose to true -> ```litellm.set_verbose = True```    
def print_verbose(print_statement):
  if litellm.set_verbose:
    print(f"LiteLLM: {print_statement}")
    if random.random() <= 0.3:
      print("Get help - https://discord.com/invite/wuPM9dRgDw")


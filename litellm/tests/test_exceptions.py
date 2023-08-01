from openai.error import AuthenticationError, InvalidRequestError, RateLimitError, OpenAIError
import os 
import sys
import traceback
sys.path.insert(0, os.path.abspath('../..'))  # Adds the parent directory to the system path
import litellm
from litellm import embedding, completion
from concurrent.futures import ThreadPoolExecutor
#### What this tests ####
#    This tests exception mapping -> trigger an exception from an llm provider -> assert if output is of the expected type


# 5 providers -> OpenAI, Azure, Anthropic, Cohere, Replicate

# 3 main types of exceptions -> - Rate Limit Errors, Context Window Errors, Auth errors (incorrect/rotated key, etc.)

# Approach: Run each model through the test -> assert if the correct error (always the same one) is triggered

models = ["gpt-3.5-turbo", "chatgpt-test", "claude-instant-1", "command-nightly", "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1"]

# Test 1: Rate Limit Errors 
def test_model(model):
    try: 
        sample_text = "how does a court case get to the Supreme Court?" * 50000
        messages = [{ "content": sample_text,"role": "user"}]
        azure = False
        if model == "chatgpt-test":
            azure = True
        print(f"model: {model}")
        response = completion(model=model, messages=messages, azure=azure)
    except RateLimitError:
        return True
    except OpenAIError: # is at least an openai error -> in case of random model errors - e.g. overloaded server
        return True
    except Exception as e:
        print(f"Uncaught Exception {model}: {type(e).__name__} - {e}")
        pass
    return False

# Repeat each model 500 times
extended_models = [model for model in models for _ in range(250)]

def worker(model):
    return test_model(model)

# Create a dictionary to store the results
counts = {True: 0, False: 0}

# Use Thread Pool Executor
with ThreadPoolExecutor(max_workers=500) as executor:
    # Use map to start the operation in thread pool
    results = executor.map(worker, extended_models)

    # Iterate over results and count True/False
    for result in results:
        counts[result] += 1

accuracy_score = counts[True]/(counts[True] + counts[False])
print(f"accuracy_score: {accuracy_score}")

# Test 2: Context Window Errors 
print("Testing Context Window Errors")
def test_model(model): # pass extremely long input
    sample_text = "how does a court case get to the Supreme Court?" * 100000
    messages = [{ "content": sample_text,"role": "user"}]
    try: 
        azure = False
        if model == "chatgpt-test":
            azure = True
        print(f"model: {model}")
        response = completion(model=model, messages=messages, azure=azure)
    except InvalidRequestError:
        return True
    except OpenAIError: # is at least an openai error -> in case of random model errors - e.g. overloaded server
        return True
    except Exception as e:
        print(f"Error Type: {type(e).__name__}")
        print(f"Uncaught Exception - {e}")
        pass
    return False

## TEST SCORE
true_val = 0
for model in models: 
    if test_model(model=model) == True:
        true_val += 1
accuracy_score = true_val/len(models)
print(f"CTX WINDOW accuracy_score: {accuracy_score}")

# Test 3: InvalidAuth Errors
def logger_fn(model_call_object: dict):
    print(f"model call details: {model_call_object}")


def test_model(model): # set the model key to an invalid key, depending on the model 
    messages = [{ "content": "Hello, how are you?","role": "user"}]
    try: 
        azure = False
        if model == "gpt-3.5-turbo":
            os.environ["OPENAI_API_KEY"] = "bad-key"
        elif model == "chatgpt-test":
            os.environ["AZURE_API_KEY"] = "bad-key"
            azure = True
        elif model == "claude-instant-1":
            os.environ["ANTHROPIC_API_KEY"] = "bad-key"
        elif model == "command-nightly":
            os.environ["COHERE_API_KEY"] = "bad-key"
        elif model == "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1":
            os.environ["REPLICATE_API_KEY"] = "bad-key"
            os.environ["REPLICATE_API_TOKEN"] = "bad-key"
        print(f"model: {model}")
        response = completion(model=model, messages=messages, azure=azure, logger_fn=logger_fn)
        print(f"response: {response}")
    except AuthenticationError as e:
        return True
    except OpenAIError: # is at least an openai error -> in case of random model errors - e.g. overloaded server
        return True
    except Exception as e:
        print(f"Uncaught Exception - {e}")
        pass
    return False

## TEST SCORE
true_val = 0
for model in models: 
    if test_model(model=model) == True:
        true_val += 1
accuracy_score = true_val/len(models)
print(f"INVALID AUTH accuracy_score: {accuracy_score}")
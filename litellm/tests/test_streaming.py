#### What this tests ####
#    This tests streaming for the completion endpoint

import sys, os, asyncio
import traceback
import time, pytest

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import litellm
from litellm import completion, acompletion

litellm.logging = False
litellm.set_verbose = False

score = 0


def logger_fn(model_call_object: dict):
    print(f"model call details: {model_call_object}")


user_message = "Hello, how are you?"
messages = [{"content": user_message, "role": "user"}]


first_openai_chunk_example = {
    "id": "chatcmpl-7zSKLBVXnX9dwgRuDYVqVVDsgh2yp",
    "object": "chat.completion.chunk",
    "created": 1694881253,
    "model": "gpt-4-0613",
    "choices": [
        {
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": ""
            },
            "finish_reason": None # it's null
        }
    ]
}

def validate_first_format(chunk):
    # write a test to make sure chunk follows the same format as first_openai_chunk_example
    assert isinstance(chunk, dict), "Chunk should be a dictionary."
    assert "id" in chunk, "Chunk should have an 'id'."
    assert isinstance(chunk['id'], str), "'id' should be a string."
    
    assert "object" in chunk, "Chunk should have an 'object'."
    assert isinstance(chunk['object'], str), "'object' should be a string."

    assert "created" in chunk, "Chunk should have a 'created'."
    assert isinstance(chunk['created'], int), "'created' should be an integer."

    assert "model" in chunk, "Chunk should have a 'model'."
    assert isinstance(chunk['model'], str), "'model' should be a string."

    assert "choices" in chunk, "Chunk should have 'choices'."
    assert isinstance(chunk['choices'], list), "'choices' should be a list."

    for choice in chunk['choices']:
        assert isinstance(choice, dict), "Each choice should be a dictionary."

        assert "index" in choice, "Each choice should have 'index'."
        assert isinstance(choice['index'], int), "'index' should be an integer."

        assert "delta" in choice, "Each choice should have 'delta'." 
        assert isinstance(choice['delta'], dict), "'delta' should be a dictionary."

        assert "role" in choice['delta'], "'delta' should have a 'role'."
        assert isinstance(choice['delta']['role'], str), "'role' should be a string."

        assert "content" in choice['delta'], "'delta' should have 'content'."
        assert isinstance(choice['delta']['content'], str), "'content' should be a string."

        assert "finish_reason" in choice, "Each choice should have 'finish_reason'."
        assert (choice['finish_reason'] is None) or isinstance(choice['finish_reason'], str), "'finish_reason' should be None or a string."

second_openai_chunk_example = {
    "id": "chatcmpl-7zSKLBVXnX9dwgRuDYVqVVDsgh2yp",
    "object": "chat.completion.chunk",
    "created": 1694881253,
    "model": "gpt-4-0613",
    "choices": [
        {
            "index": 0,
            "delta": {
                "content": "Hello"
            },
            "finish_reason": None # it's null
        }
    ]
}

def validate_second_format(chunk):
    assert isinstance(chunk, dict), "Chunk should be a dictionary."
    assert "id" in chunk, "Chunk should have an 'id'."
    assert isinstance(chunk['id'], str), "'id' should be a string."
    
    assert "object" in chunk, "Chunk should have an 'object'."
    assert isinstance(chunk['object'], str), "'object' should be a string."

    assert "created" in chunk, "Chunk should have a 'created'."
    assert isinstance(chunk['created'], int), "'created' should be an integer."

    assert "model" in chunk, "Chunk should have a 'model'."
    assert isinstance(chunk['model'], str), "'model' should be a string."

    assert "choices" in chunk, "Chunk should have 'choices'."
    assert isinstance(chunk['choices'], list), "'choices' should be a list."

    for choice in chunk['choices']:
        assert isinstance(choice, dict), "Each choice should be a dictionary."

        assert "index" in choice, "Each choice should have 'index'."
        assert isinstance(choice['index'], int), "'index' should be an integer."

        assert "delta" in choice, "Each choice should have 'delta'." 
        assert isinstance(choice['delta'], dict), "'delta' should be a dictionary."

        assert "content" in choice['delta'], "'delta' should have 'content'."
        assert isinstance(choice['delta']['content'], str), "'content' should be a string."

        assert "finish_reason" in choice, "Each choice should have 'finish_reason'."
        assert (choice['finish_reason'] is None) or isinstance(choice['finish_reason'], str), "'finish_reason' should be None or a string."

last_openai_chunk_example = {
    "id": "chatcmpl-7zSKLBVXnX9dwgRuDYVqVVDsgh2yp",
    "object": "chat.completion.chunk",
    "created": 1694881253,
    "model": "gpt-4-0613",
    "choices": [
        {
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }
    ]
}

def validate_last_format(chunk):
    assert isinstance(chunk, dict), "Chunk should be a dictionary."
    assert "id" in chunk, "Chunk should have an 'id'."
    assert isinstance(chunk['id'], str), "'id' should be a string."
    
    assert "object" in chunk, "Chunk should have an 'object'."
    assert isinstance(chunk['object'], str), "'object' should be a string."

    assert "created" in chunk, "Chunk should have a 'created'."
    assert isinstance(chunk['created'], int), "'created' should be an integer."

    assert "model" in chunk, "Chunk should have a 'model'."
    assert isinstance(chunk['model'], str), "'model' should be a string."

    assert "choices" in chunk, "Chunk should have 'choices'."
    assert isinstance(chunk['choices'], list), "'choices' should be a list."

    for choice in chunk['choices']:
        assert isinstance(choice, dict), "Each choice should be a dictionary."

        assert "index" in choice, "Each choice should have 'index'."
        assert isinstance(choice['index'], int), "'index' should be an integer."

        assert "delta" in choice, "Each choice should have 'delta'." 
        assert isinstance(choice['delta'], dict), "'delta' should be a dictionary."

        assert "finish_reason" in choice, "Each choice should have 'finish_reason'."
        assert isinstance(choice['finish_reason'], str), "'finish_reason' should be a string."

def streaming_format_tests(idx, chunk):
    extracted_chunk = "" 
    finished = False
    print(f"chunk: {chunk}")
    if idx == 0: # ensure role assistant is set 
        validate_first_format(chunk=chunk)
        role = chunk["choices"][0]["delta"]["role"]
        assert role == "assistant"
    elif idx == 1: # second chunk 
        validate_second_format(chunk=chunk)
    if idx != 0: # ensure no role
        if "role" in chunk["choices"][0]["delta"]:
            raise Exception("role should not exist after first chunk")
    if chunk["choices"][0]["finish_reason"]: # ensure finish reason is only in last chunk
        validate_last_format(chunk=chunk)
        finished = True
    if "content" in chunk["choices"][0]["delta"]:
        extracted_chunk = chunk["choices"][0]["delta"]["content"]
    return extracted_chunk, finished

def test_completion_cohere_stream():
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "how does a court case get to the Supreme Court?",
            },
        ]
        response = completion(
            model="command-nightly", messages=messages, stream=True, max_tokens=50
        )
        complete_response = ""
        # Add any assertions here to check the response
        for idx, chunk in enumerate(response):
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
        if complete_response.strip() == "": 
            raise Exception("Empty response received")
        print(f"completion_response: {complete_response}")
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
        
# test_completion_cohere_stream()

# test on openai completion call
def test_openai_text_completion_call():
    try:
        response = completion(
            model="text-davinci-003", messages=messages, stream=True, logger_fn=logger_fn
        )
        complete_response = ""
        start_time = time.time()
        for idx, chunk in enumerate(response):
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
        if complete_response.strip() == "": 
            raise Exception("Empty response received")
    except:
        pytest.fail(f"error occurred: {traceback.format_exc()}")

test_openai_text_completion_call()

# # test on ai21 completion call
def ai21_completion_call():
    try:
        response = completion(
            model="j2-ultra", messages=messages, stream=True, logger_fn=logger_fn
        )
        print(f"response: {response}")
        complete_response = ""
        start_time = time.time()
        for idx, chunk in enumerate(response):
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
        if complete_response.strip() == "": 
            raise Exception("Empty response received")
        print(f"completion_response: {complete_response}")
    except:
        pytest.fail(f"error occurred: {traceback.format_exc()}")

# ai21_completion_call()
# test on openai completion call
def test_openai_chat_completion_call():
    try:
        response = completion(
            model="gpt-3.5-turbo", messages=messages, stream=True, logger_fn=logger_fn
        )
        complete_response = ""
        start_time = time.time()
        for idx, chunk in enumerate(response):
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
            # print(f'complete_chunk: {complete_response}')
        if complete_response.strip() == "": 
            raise Exception("Empty response received")
        print(f"complete response: {complete_response}")
    except:
        print(f"error occurred: {traceback.format_exc()}")
        pass

# test_openai_chat_completion_call()

# # test on together ai completion call - starcoder
def test_together_ai_completion_call_starcoder():
    try:
        start_time = time.time()
        response = completion(
            model="together_ai/bigcode/starcoder",
            messages=messages,
            logger_fn=logger_fn,
            stream=True,
        )
        complete_response = ""
        print(f"returned response object: {response}")
        for idx, chunk in enumerate(response):
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
        if complete_response == "":
            raise Exception("Empty response received")
        print(f"complete response: {complete_response}")
    except:
        print(f"error occurred: {traceback.format_exc()}")
        pass
# test_together_ai_completion_call_starcoder()
# test on aleph alpha completion call - commented out as it's expensive to run this on circle ci for every build
# def test_aleph_alpha_call():
#     try:
#         start_time = time.time()
#         response = completion(
#             model="luminous-base",
#             messages=messages,
#             logger_fn=logger_fn,
#             stream=True,
#         )
#         complete_response = ""
#         print(f"returned response object: {response}")
#         for chunk in response:
#             chunk_time = time.time()
#             complete_response += (
#                 chunk["choices"][0]["delta"]["content"]
#                 if len(chunk["choices"][0]["delta"].keys()) > 0
#                 else ""
#             )
#             if len(complete_response) > 0:
#                 print(complete_response)
#         if complete_response == "":
#             raise Exception("Empty response received")
#     except:
#         print(f"error occurred: {traceback.format_exc()}")
#         pass
#### Test Async streaming 

# # test on ai21 completion call
async def ai21_async_completion_call():
    try:
        response = completion(
            model="j2-ultra", messages=messages, stream=True, logger_fn=logger_fn
        )
        print(f"response: {response}")
        complete_response = ""
        start_time = time.time()
        # Change for loop to async for loop
        idx = 0
        async for chunk in response:
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
            idx += 1
        if complete_response.strip() == "": 
            raise Exception("Empty response received")
        print(f"complete response: {complete_response}")
    except:
        print(f"error occurred: {traceback.format_exc()}")
        pass

# asyncio.run(ai21_async_completion_call())

async def completion_call():
    try:
        response = completion(
            model="gpt-3.5-turbo", messages=messages, stream=True, logger_fn=logger_fn
        )
        print(f"response: {response}")
        complete_response = ""
        start_time = time.time()
        # Change for loop to async for loop
        idx = 0
        async for chunk in response:
            chunk, finished = streaming_format_tests(idx, chunk)
            if finished:
                break
            complete_response += chunk
            idx += 1
        if complete_response.strip() == "": 
            raise Exception("Empty response received")
        print(f"complete response: {complete_response}")
    except:
        print(f"error occurred: {traceback.format_exc()}")
        pass

# asyncio.run(completion_call())

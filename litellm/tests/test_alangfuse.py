import json
import sys
import os
import io, asyncio

import logging

logging.basicConfig(level=logging.DEBUG)
sys.path.insert(0, os.path.abspath("../.."))

from litellm import completion
import litellm

litellm.num_retries = 3
litellm.success_callback = ["langfuse"]
os.environ["LANGFUSE_DEBUG"] = "True"
import time
import pytest


def search_logs(log_file_path, num_good_logs=1):
    """
    Searches the given log file for logs containing the "/api/public" string.

    Parameters:
    - log_file_path (str): The path to the log file to be searched.

    Returns:
    - None

    Raises:
    - Exception: If there are any bad logs found in the log file.
    """
    import re

    print("\n searching logs")
    bad_logs = []
    good_logs = []
    all_logs = []
    try:
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            print(f"searching logslines: {lines}")
            for line in lines:
                all_logs.append(line.strip())
                if "/api/public" in line:
                    print("Found log with /api/public:")
                    print(line.strip())
                    print("\n\n")
                    match = re.search(
                        r'"POST /api/public/ingestion HTTP/1.1" (\d+) (\d+)',
                        line,
                    )
                    if match:
                        status_code = int(match.group(1))
                        print("STATUS CODE", status_code)
                        if (
                            status_code != 200
                            and status_code != 201
                            and status_code != 207
                        ):
                            print("got a BAD log")
                            bad_logs.append(line.strip())
                        else:
                            good_logs.append(line.strip())
        print("\nBad Logs")
        print(bad_logs)
        if len(bad_logs) > 0:
            raise Exception(f"bad logs, Bad logs = {bad_logs}")
        assert (
            len(good_logs) == num_good_logs
        ), f"Did not get expected number of good logs, expected {num_good_logs}, got {len(good_logs)}. All logs \n {all_logs}"
        print("\nGood Logs")
        print(good_logs)
        if len(good_logs) <= 0:
            raise Exception(
                f"There were no Good Logs from Langfuse. No logs with /api/public status 200. \nAll logs:{all_logs}"
            )

    except Exception as e:
        raise e


def pre_langfuse_setup():
    """
    Set up the logging for the 'pre_langfuse_setup' function.
    """
    # sends logs to langfuse.log
    import logging

    # Configure the logging to write to a file
    logging.basicConfig(filename="langfuse.log", level=logging.DEBUG)
    logger = logging.getLogger()

    # Add a FileHandler to the logger
    file_handler = logging.FileHandler("langfuse.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return


def test_langfuse_logging_async():
    # this tests time added to make langfuse logging calls, vs just acompletion calls
    try:
        pre_langfuse_setup()
        litellm.set_verbose = True

        # Make 5 calls with an empty success_callback
        litellm.success_callback = []
        start_time_empty_callback = asyncio.run(make_async_calls())
        print("done with no callback test")

        print("starting langfuse test")
        # Make 5 calls with success_callback set to "langfuse"
        litellm.success_callback = ["langfuse"]
        start_time_langfuse = asyncio.run(make_async_calls())
        print("done with langfuse test")

        # Compare the time for both scenarios
        print(f"Time taken with success_callback='langfuse': {start_time_langfuse}")
        print(f"Time taken with empty success_callback: {start_time_empty_callback}")

        # assert the diff is not more than 1 second - this was 5 seconds before the fix
        assert abs(start_time_langfuse - start_time_empty_callback) < 1

    except litellm.Timeout as e:
        pass
    except Exception as e:
        pytest.fail(f"An exception occurred - {e}")


async def make_async_calls():
    tasks = []
    for _ in range(5):
        task = asyncio.create_task(
            litellm.acompletion(
                model="azure/chatgpt-v-2",
                messages=[{"role": "user", "content": "This is a test"}],
                max_tokens=5,
                temperature=0.7,
                timeout=5,
                user="langfuse_latency_test_user",
                mock_response="It's simple to use and easy to get started",
            )
        )
        tasks.append(task)

    # Measure the start time before running the tasks
    start_time = asyncio.get_event_loop().time()

    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)

    # Print the responses when tasks return
    for idx, response in enumerate(responses):
        print(f"Response from Task {idx + 1}: {response}")

    # Calculate the total time taken
    total_time = asyncio.get_event_loop().time() - start_time

    return total_time


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_langfuse_logging_without_request_response(stream):
    try:
        import uuid

        _unique_trace_name = f"litellm-test-{str(uuid.uuid4())}"
        litellm.set_verbose = True
        litellm.turn_off_message_logging = True
        litellm.success_callback = ["langfuse"]
        response = await litellm.acompletion(
            model="gpt-3.5-turbo",
            mock_response="It's simple to use and easy to get started",
            messages=[{"role": "user", "content": "Hi 👋 - i'm claude"}],
            max_tokens=10,
            temperature=0.2,
            stream=stream,
            metadata={"trace_id": _unique_trace_name},
        )
        print(response)
        if stream:
            async for chunk in response:
                print(chunk)

        await asyncio.sleep(3)

        import langfuse

        langfuse_client = langfuse.Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        )

        # get trace with _unique_trace_name
        trace = langfuse_client.get_generations(trace_id=_unique_trace_name)

        print("trace_from_langfuse", trace)

        _trace_data = trace.data

        assert _trace_data[0].input == {"messages": "redacted-by-litellm"}
        assert _trace_data[0].output == {
            "role": "assistant",
            "content": "redacted-by-litellm",
            "function_call": None,
            "tool_calls": None,
        }

    except Exception as e:
        pytest.fail(f"An exception occurred - {e}")


@pytest.mark.skip(reason="beta test - checking langfuse output")
def test_langfuse_logging():
    try:
        pre_langfuse_setup()
        litellm.set_verbose = True
        response = completion(
            model="claude-instant-1.2",
            messages=[{"role": "user", "content": "Hi 👋 - i'm claude"}],
            max_tokens=10,
            temperature=0.2,
        )
        print(response)
        # time.sleep(5)
        # # check langfuse.log to see if there was a failed response
        # search_logs("langfuse.log")

    except litellm.Timeout as e:
        pass
    except Exception as e:
        pytest.fail(f"An exception occurred - {e}")


# test_langfuse_logging()


@pytest.mark.skip(reason="beta test - checking langfuse output")
def test_langfuse_logging_stream():
    try:
        litellm.set_verbose = True
        response = completion(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "this is a streaming test for llama2 + langfuse",
                }
            ],
            max_tokens=20,
            temperature=0.2,
            stream=True,
        )
        print(response)
        for chunk in response:
            pass
            # print(chunk)
    except litellm.Timeout as e:
        pass
    except Exception as e:
        print(e)


# test_langfuse_logging_stream()


@pytest.mark.skip(reason="beta test - checking langfuse output")
def test_langfuse_logging_custom_generation_name():
    try:
        litellm.set_verbose = True
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi 👋 - i'm claude"}],
            max_tokens=10,
            metadata={
                "langfuse/foo": "bar",
                "langsmith/fizz": "buzz",
                "prompt_hash": "asdf98u0j9131123",
                "generation_name": "ishaan-test-generation",
                "generation_id": "gen-id22",
                "trace_id": "trace-id22",
                "trace_user_id": "user-id2",
            },
        )
        print(response)
    except litellm.Timeout as e:
        pass
    except Exception as e:
        pytest.fail(f"An exception occurred - {e}")
        print(e)


# test_langfuse_logging_custom_generation_name()


@pytest.mark.skip(reason="beta test - checking langfuse output")
def test_langfuse_logging_embedding():
    try:
        litellm.set_verbose = True
        litellm.success_callback = ["langfuse"]
        response = litellm.embedding(
            model="text-embedding-ada-002",
            input=["gm", "ishaan"],
        )
        print(response)
    except litellm.Timeout as e:
        pass
    except Exception as e:
        pytest.fail(f"An exception occurred - {e}")
        print(e)


@pytest.mark.skip(reason="beta test - checking langfuse output")
def test_langfuse_logging_function_calling():
    litellm.set_verbose = True
    function1 = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]
    try:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "what's the weather in boston"}],
            temperature=0.1,
            functions=function1,
        )
        print(response)
    except litellm.Timeout as e:
        pass
    except Exception as e:
        print(e)


# test_langfuse_logging_function_calling()


def test_langfuse_existing_trace_id():
    """
    When existing trace id is passed, don't set trace params -> prevents overwriting the trace

    Pass 1 logging object with a trace

    Pass 2nd logging object with the trace id

    Assert no changes to the trace
    """
    # Test - if the logs were sent to the correct team on langfuse
    import litellm, datetime
    from litellm.integrations.langfuse import LangFuseLogger

    langfuse_Logger = LangFuseLogger(
        langfuse_public_key=os.getenv("LANGFUSE_PROJECT2_PUBLIC"),
        langfuse_secret=os.getenv("LANGFUSE_PROJECT2_SECRET"),
    )
    litellm.success_callback = ["langfuse"]

    # langfuse_args = {'kwargs': { 'start_time':  'end_time': datetime.datetime(2024, 5, 1, 7, 31, 29, 903685), 'user_id': None, 'print_verbose': <function print_verbose at 0x109d1f420>, 'level': 'DEFAULT', 'status_message': None}
    response_obj = litellm.ModelResponse(
        id="chatcmpl-9K5HUAbVRqFrMZKXL0WoC295xhguY",
        choices=[
            litellm.Choices(
                finish_reason="stop",
                index=0,
                message=litellm.Message(
                    content="I'm sorry, I am an AI assistant and do not have real-time information. I recommend checking a reliable weather website or app for the most up-to-date weather information in Boston.",
                    role="assistant",
                ),
            )
        ],
        created=1714573888,
        model="gpt-3.5-turbo-0125",
        object="chat.completion",
        system_fingerprint="fp_3b956da36b",
        usage=litellm.Usage(completion_tokens=37, prompt_tokens=14, total_tokens=51),
    )

    ### NEW TRACE ###
    message = [{"role": "user", "content": "what's the weather in boston"}]
    langfuse_args = {
        "response_obj": response_obj,
        "kwargs": {
            "model": "gpt-3.5-turbo",
            "litellm_params": {
                "acompletion": False,
                "api_key": None,
                "force_timeout": 600,
                "logger_fn": None,
                "verbose": False,
                "custom_llm_provider": "openai",
                "api_base": "https://api.openai.com/v1/",
                "litellm_call_id": "508113a1-c6f1-48ce-a3e1-01c6cce9330e",
                "model_alias_map": {},
                "completion_call_id": None,
                "metadata": None,
                "model_info": None,
                "proxy_server_request": None,
                "preset_cache_key": None,
                "no-log": False,
                "stream_response": {},
            },
            "messages": message,
            "optional_params": {"temperature": 0.1, "extra_body": {}},
            "start_time": "2024-05-01 07:31:27.986164",
            "stream": False,
            "user": None,
            "call_type": "completion",
            "litellm_call_id": "508113a1-c6f1-48ce-a3e1-01c6cce9330e",
            "completion_start_time": "2024-05-01 07:31:29.903685",
            "temperature": 0.1,
            "extra_body": {},
            "input": [{"role": "user", "content": "what's the weather in boston"}],
            "api_key": "my-api-key",
            "additional_args": {
                "complete_input_dict": {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": "what's the weather in boston"}
                    ],
                    "temperature": 0.1,
                    "extra_body": {},
                }
            },
            "log_event_type": "successful_api_call",
            "end_time": "2024-05-01 07:31:29.903685",
            "cache_hit": None,
            "response_cost": 6.25e-05,
        },
        "start_time": datetime.datetime(2024, 5, 1, 7, 31, 27, 986164),
        "end_time": datetime.datetime(2024, 5, 1, 7, 31, 29, 903685),
        "user_id": None,
        "print_verbose": litellm.print_verbose,
        "level": "DEFAULT",
        "status_message": None,
    }

    langfuse_response_object = langfuse_Logger.log_event(**langfuse_args)

    import langfuse

    langfuse_client = langfuse.Langfuse(
        public_key=os.getenv("LANGFUSE_PROJECT2_PUBLIC"),
        secret_key=os.getenv("LANGFUSE_PROJECT2_SECRET"),
    )

    trace_id = langfuse_response_object["trace_id"]

    langfuse_client.flush()

    time.sleep(2)

    print(langfuse_client.get_trace(id=trace_id))

    initial_langfuse_trace = langfuse_client.get_trace(id=trace_id)

    ### EXISTING TRACE ###

    new_metadata = {"existing_trace_id": trace_id}
    new_messages = [{"role": "user", "content": "What do you know?"}]
    new_response_obj = litellm.ModelResponse(
        id="chatcmpl-9K5HUAbVRqFrMZKXL0WoC295xhguY",
        choices=[
            litellm.Choices(
                finish_reason="stop",
                index=0,
                message=litellm.Message(
                    content="What do I know?",
                    role="assistant",
                ),
            )
        ],
        created=1714573888,
        model="gpt-3.5-turbo-0125",
        object="chat.completion",
        system_fingerprint="fp_3b956da36b",
        usage=litellm.Usage(completion_tokens=37, prompt_tokens=14, total_tokens=51),
    )
    langfuse_args = {
        "response_obj": new_response_obj,
        "kwargs": {
            "model": "gpt-3.5-turbo",
            "litellm_params": {
                "acompletion": False,
                "api_key": None,
                "force_timeout": 600,
                "logger_fn": None,
                "verbose": False,
                "custom_llm_provider": "openai",
                "api_base": "https://api.openai.com/v1/",
                "litellm_call_id": "508113a1-c6f1-48ce-a3e1-01c6cce9330e",
                "model_alias_map": {},
                "completion_call_id": None,
                "metadata": new_metadata,
                "model_info": None,
                "proxy_server_request": None,
                "preset_cache_key": None,
                "no-log": False,
                "stream_response": {},
            },
            "messages": new_messages,
            "optional_params": {"temperature": 0.1, "extra_body": {}},
            "start_time": "2024-05-01 07:31:27.986164",
            "stream": False,
            "user": None,
            "call_type": "completion",
            "litellm_call_id": "508113a1-c6f1-48ce-a3e1-01c6cce9330e",
            "completion_start_time": "2024-05-01 07:31:29.903685",
            "temperature": 0.1,
            "extra_body": {},
            "input": [{"role": "user", "content": "what's the weather in boston"}],
            "api_key": "my-api-key",
            "additional_args": {
                "complete_input_dict": {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": "what's the weather in boston"}
                    ],
                    "temperature": 0.1,
                    "extra_body": {},
                }
            },
            "log_event_type": "successful_api_call",
            "end_time": "2024-05-01 07:31:29.903685",
            "cache_hit": None,
            "response_cost": 6.25e-05,
        },
        "start_time": datetime.datetime(2024, 5, 1, 7, 31, 27, 986164),
        "end_time": datetime.datetime(2024, 5, 1, 7, 31, 29, 903685),
        "user_id": None,
        "print_verbose": litellm.print_verbose,
        "level": "DEFAULT",
        "status_message": None,
    }

    langfuse_response_object = langfuse_Logger.log_event(**langfuse_args)

    new_trace_id = langfuse_response_object["trace_id"]

    assert new_trace_id == trace_id

    langfuse_client.flush()

    time.sleep(2)

    print(langfuse_client.get_trace(id=trace_id))

    new_langfuse_trace = langfuse_client.get_trace(id=trace_id)

    assert dict(initial_langfuse_trace) == dict(new_langfuse_trace)


def test_langfuse_logging_tool_calling():
    litellm.set_verbose = True

    def get_current_weather(location, unit="fahrenheit"):
        """Get the current weather in a given location"""
        if "tokyo" in location.lower():
            return json.dumps(
                {"location": "Tokyo", "temperature": "10", "unit": "celsius"}
            )
        elif "san francisco" in location.lower():
            return json.dumps(
                {"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"}
            )
        elif "paris" in location.lower():
            return json.dumps(
                {"location": "Paris", "temperature": "22", "unit": "celsius"}
            )
        else:
            return json.dumps({"location": location, "temperature": "unknown"})

    messages = [
        {
            "role": "user",
            "content": "What's the weather like in San Francisco, Tokyo, and Paris?",
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    response = litellm.completion(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    print("\nLLM Response1:\n", response)
    response_message = response.choices[0].message
    tool_calls = response.choices[0].message.tool_calls


# test_langfuse_logging_tool_calling()

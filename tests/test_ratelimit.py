# %%
import asyncio
import os
import pytest
import random
from typing import Any

from pydantic import BaseModel
from litellm import utils, Router

COMPLETION_TOKENS = 5
base_model_list = [
    {
        "model_name": "gpt-3.5-turbo",
        "litellm_params": {
            "model": "gpt-3.5-turbo",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "max_tokens": COMPLETION_TOKENS,
        },
    }
]


class RouterConfig(BaseModel):
    rpm: int
    tpm: int


@pytest.fixture(scope="function")
def router_factory():
    def create_router(rpm, tpm):
        model_list = base_model_list.copy()
        model_list[0]["rpm"] = rpm
        model_list[0]["tpm"] = tpm
        return Router(
            model_list=model_list,
            routing_strategy="usage-based-routing",
            debug_level="DEBUG",
        )

    return create_router


def generate_list_of_messages(num_messages):
    """
    create num_messages new chat conversations
    """
    return [
        [{"role": "user", "content": f"{i}. Hey, how's it going? {random.random()}"}]
        for i in range(num_messages)
    ]


def calculate_limits(list_of_messages):
    """
    Return the min rpm and tpm level that would let all messages in list_of_messages be sent this minute
    """
    rpm = len(list_of_messages)
    tpm = sum((utils.token_counter(messages=m) + COMPLETION_TOKENS for m in list_of_messages))
    return rpm, tpm


async def async_call(router: Router, list_of_messages) -> Any:
    tasks = [router.acompletion(model="gpt-3.5-turbo", messages=m) for m in list_of_messages]
    return await asyncio.gather(*tasks)


def sync_call(router: Router, list_of_messages) -> Any:
    return [router.completion(model="gpt-3.5-turbo", messages=m) for m in list_of_messages]


class ExpectNoException(Exception):
    pass


@pytest.mark.parametrize(
    "num_try_send, num_allowed_send",
    [
        (2, 2),  # sending as many as allowed, ExpectNoException
        # (10, 10),  # sending as many as allowed, ExpectNoException
        (3, 2),  # Sending more than allowed, ValueError
        # (10, 9),  # Sending more than allowed, ValueError
    ],
)
@pytest.mark.parametrize("sync_mode", [True, False])  # Use parametrization for sync/async
def test_rate_limit(router_factory, num_try_send, num_allowed_send, sync_mode):
    """
    Check if router.completion and router.acompletion can send more messages than they've been limited to.
    Args:
        router_factory: makes new router object, without any shared Global state
        num_try_send (int): number of messages to try to send
        num_allowed_send (int): max number of messages allowed to be sent in 1 minute
        sync_mode (bool): if making sync (router.completion) or async (router.acompletion)
    Raises:
        ValueError: Error router throws when it hits rate limits
        ExpectNoException: Signfies that no other error has happened. A NOP
    """
    # Can send more messages then we're going to; so don't expect a rate limit error
    expected_exception = ExpectNoException if num_try_send <= num_allowed_send else ValueError

    list_of_messages = generate_list_of_messages(max(num_try_send, num_allowed_send))
    rpm, tpm = calculate_limits(list_of_messages[:num_allowed_send])
    list_of_messages = list_of_messages[:num_try_send]
    router = router_factory(rpm, tpm)

    with pytest.raises(expected_exception) as excinfo:  # asserts correct type raised
        if sync_mode:
            results = sync_call(router, list_of_messages)
        else:
            results = asyncio.run(async_call(router, list_of_messages))
        print(results)
        if len([i for i in results if i is not None]) != num_try_send:
            # since not all results got returned, raise rate limit error
            raise ValueError("No deployments available for selected model")
        raise ExpectNoException

    print(expected_exception, excinfo)
    if expected_exception is ValueError:
        assert "No deployments available for selected model" in str(excinfo.value)
    else:
        assert len([i for i in results if i is not None]) == num_try_send

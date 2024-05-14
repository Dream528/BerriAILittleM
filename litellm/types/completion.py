from typing import List, Optional, Union, Iterable

from pydantic import ConfigDict, BaseModel, validator, VERSION

from typing_extensions import Literal, Required, TypedDict


# Function to get Pydantic version
def is_pydantic_v2() -> int:
    return int(VERSION.split(".")[0])


def get_model_config() -> ConfigDict:
    # Version-specific configuration
    if is_pydantic_v2() >= 2:
        model_config = ConfigDict(extra="allow", protected_namespaces=())  # type: ignore
    else:
        model_config = ConfigDict(extra="allow")  # No protected_namespaces for v1

    return model_config


class ChatCompletionSystemMessageParam(TypedDict, total=False):
    content: Required[str]
    """The contents of the system message."""

    role: Required[Literal["system"]]
    """The role of the messages author, in this case `system`."""

    name: str
    """An optional name for the participant.

    Provides the model information to differentiate between participants of the same
    role.
    """


class ChatCompletionContentPartTextParam(TypedDict, total=False):
    text: Required[str]
    """The text content."""

    type: Required[Literal["text"]]
    """The type of the content part."""


class ImageURL(TypedDict, total=False):
    url: Required[str]
    """Either a URL of the image or the base64 encoded image data."""

    detail: Literal["auto", "low", "high"]
    """Specifies the detail level of the image.

    Learn more in the
    [Vision guide](https://platform.openai.com/docs/guides/vision/low-or-high-fidelity-image-understanding).
    """


class ChatCompletionContentPartImageParam(TypedDict, total=False):
    image_url: Required[ImageURL]

    type: Required[Literal["image_url"]]
    """The type of the content part."""


ChatCompletionContentPartParam = Union[
    ChatCompletionContentPartTextParam, ChatCompletionContentPartImageParam
]


class ChatCompletionUserMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ChatCompletionContentPartParam]]]
    """The contents of the user message."""

    role: Required[Literal["user"]]
    """The role of the messages author, in this case `user`."""

    name: str
    """An optional name for the participant.

    Provides the model information to differentiate between participants of the same
    role.
    """


class FunctionCall(TypedDict, total=False):
    arguments: Required[str]
    """
    The arguments to call the function with, as generated by the model in JSON
    format. Note that the model does not always generate valid JSON, and may
    hallucinate parameters not defined by your function schema. Validate the
    arguments in your code before calling your function.
    """

    name: Required[str]
    """The name of the function to call."""


class Function(TypedDict, total=False):
    arguments: Required[str]
    """
    The arguments to call the function with, as generated by the model in JSON
    format. Note that the model does not always generate valid JSON, and may
    hallucinate parameters not defined by your function schema. Validate the
    arguments in your code before calling your function.
    """

    name: Required[str]
    """The name of the function to call."""


class ChatCompletionToolMessageParam(TypedDict, total=False):
    content: Required[str]
    """The contents of the tool message."""

    role: Required[Literal["tool"]]
    """The role of the messages author, in this case `tool`."""

    tool_call_id: Required[str]
    """Tool call that this message is responding to."""


class ChatCompletionFunctionMessageParam(TypedDict, total=False):
    content: Required[Optional[str]]
    """The contents of the function message."""

    name: Required[str]
    """The name of the function to call."""

    role: Required[Literal["function"]]
    """The role of the messages author, in this case `function`."""


class ChatCompletionMessageToolCallParam(TypedDict, total=False):
    id: Required[str]
    """The ID of the tool call."""

    function: Required[Function]
    """The function that the model called."""

    type: Required[Literal["function"]]
    """The type of the tool. Currently, only `function` is supported."""


class ChatCompletionAssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    """The role of the messages author, in this case `assistant`."""

    content: Optional[str]
    """The contents of the assistant message.

    Required unless `tool_calls` or `function_call` is specified.
    """

    function_call: FunctionCall
    """Deprecated and replaced by `tool_calls`.

    The name and arguments of a function that should be called, as generated by the
    model.
    """

    name: str
    """An optional name for the participant.

    Provides the model information to differentiate between participants of the same
    role.
    """

    tool_calls: Iterable[ChatCompletionMessageToolCallParam]
    """The tool calls generated by the model, such as function calls."""


ChatCompletionMessageParam = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionFunctionMessageParam,
    ChatCompletionToolMessageParam,
]


class CompletionRequest(BaseModel):
    model: str
    messages: List[str] = []
    timeout: Optional[Union[float, int]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    stream: Optional[bool] = None
    stop: Optional[dict] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[dict] = None
    user: Optional[str] = None
    response_format: Optional[dict] = None
    seed: Optional[int] = None
    tools: Optional[List[str]] = None
    tool_choice: Optional[str] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None
    deployment_id: Optional[str] = None
    functions: Optional[List[str]] = None
    function_call: Optional[str] = None
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    api_key: Optional[str] = None
    model_list: Optional[List[str]] = None

    model_config = get_model_config()

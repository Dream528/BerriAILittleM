from typing import TypedDict, Any, Union, Optional, Literal, List
import json
from typing_extensions import (
    Self,
    Protocol,
    TypeGuard,
    override,
    get_origin,
    runtime_checkable,
    Required,
)


class SystemContentBlock(TypedDict):
    text: str


class ImageSourceBlock(TypedDict):
    bytes: Optional[bytes]


class ImageBlock(TypedDict):
    format: Literal["png", "jpeg", "gif", "webp"]
    source: ImageSourceBlock


class ToolResultContentBlock(TypedDict, total=False):
    image: ImageBlock
    json: dict
    text: str


class ToolResultBlock(TypedDict, total=False):
    content: Required[ToolResultContentBlock]
    toolUseId: Required[str]
    status: Literal["success", "error"]


class ToolUseBlock(TypedDict):
    input: dict
    name: str
    toolUseId: str


class ContentBlock(TypedDict, total=False):
    text: str
    image: ImageBlock
    toolResult: ToolResultBlock
    toolUse: ToolUseBlock


class MessageBlock(TypedDict):
    content: List[ContentBlock]
    role: Literal["user", "assistant"]


class ToolInputSchemaBlock(TypedDict):
    json: Optional[dict]


class ToolSpecBlock(TypedDict, total=False):
    inputSchema: Required[ToolInputSchemaBlock]
    name: Required[str]
    description: str


class ToolBlock(TypedDict):
    toolSpec: Optional[ToolSpecBlock]


class SpecificToolChoiceBlock(TypedDict):
    name: str


class ToolConfigBlock(TypedDict, total=False):
    tools: Required[List[ToolBlock]]
    toolChoice: Union[str, SpecificToolChoiceBlock]


class RequestObject(TypedDict, total=False):
    additionalModelRequestFields: dict
    additionalModelResponseFieldPaths: List[str]
    inferenceConfig: dict
    messages: Required[List[MessageBlock]]
    system: List[SystemContentBlock]
    toolConfig: ToolConfigBlock


class GenericStreamingChunk(TypedDict):
    text: Required[str]
    is_finished: Required[bool]
    finish_reason: Required[str]


class Document(TypedDict):
    title: str
    snippet: str


class ServerSentEvent:
    def __init__(
        self,
        *,
        event: Optional[str] = None,
        data: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None,
    ) -> None:
        if data is None:
            data = ""

        self._id = id
        self._data = data
        self._event = event or None
        self._retry = retry

    @property
    def event(self) -> Optional[str]:
        return self._event

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def retry(self) -> Optional[int]:
        return self._retry

    @property
    def data(self) -> str:
        return self._data

    def json(self) -> Any:
        return json.loads(self.data)

    @override
    def __repr__(self) -> str:
        return f"ServerSentEvent(event={self.event}, data={self.data}, id={self.id}, retry={self.retry})"

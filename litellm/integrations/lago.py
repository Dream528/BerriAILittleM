# What is this?
## On Success events log cost to Lago - https://github.com/BerriAI/litellm/issues/3639

import dotenv, os, json
import litellm
import traceback, httpx
from litellm.integrations.custom_logger import CustomLogger
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler, HTTPHandler
import uuid
from typing import Optional


def get_utc_datetime():
    import datetime as dt
    from datetime import datetime

    if hasattr(dt, "UTC"):
        return datetime.now(dt.UTC)  # type: ignore
    else:
        return datetime.utcnow()  # type: ignore


class LagoLogger(CustomLogger):
    def __init__(self) -> None:
        super().__init__()
        self.validate_environment()
        self.async_http_handler = AsyncHTTPHandler()
        self.sync_http_handler = HTTPHandler()

    def validate_environment(self):
        """
        Expects
        LAGO_API_BASE,
        LAGO_API_KEY,

        in the environment
        """
        missing_keys = []
        if os.getenv("LAGO_API_KEY", None) is None:
            missing_keys.append("LAGO_API_KEY")

        if os.getenv("LAGO_API_BASE", None) is None:
            missing_keys.append("LAGO_API_BASE")

        if os.getenv("LAGO_API_EVENT_CODE", None) is None:
            missing_keys.append("LAGO_API_EVENT_CODE")

        if len(missing_keys) > 0:
            raise Exception("Missing keys={} in environment.".format(missing_keys))

    def _common_logic(self, kwargs: dict, response_obj) -> dict:
        call_id = response_obj.get("id", kwargs.get("litellm_call_id"))
        dt = get_utc_datetime().isoformat()
        cost = kwargs.get("response_cost", None)
        model = kwargs.get("model")
        usage = {}

        if (
            isinstance(response_obj, litellm.ModelResponse)
            or isinstance(response_obj, litellm.EmbeddingResponse)
        ) and hasattr(response_obj, "usage"):
            usage = {
                "prompt_tokens": response_obj["usage"].get("prompt_tokens", 0),
                "completion_tokens": response_obj["usage"].get("completion_tokens", 0),
                "total_tokens": response_obj["usage"].get("total_tokens"),
            }

        litellm_params = kwargs.get("litellm_params", {}) or {}
        proxy_server_request = litellm_params.get("proxy_server_request") or {}
        end_user_id = proxy_server_request.get("body", {}).get("user", None)
        user_id = litellm_params["metadata"].get("user_api_key_user_id", None)
        team_id = litellm_params["metadata"].get("user_api_key_team_id", None)
        org_id = litellm_params["metadata"].get("user_api_key_org_id", None)

        if end_user_id is None:
            raise Exception("LAGO: user is required")

        return {
            "event": {
                "transaction_id": str(uuid.uuid4()),
                "external_customer_id": end_user_id,
                "code": os.getenv("LAGO_API_EVENT_CODE"),
                "properties": {"model": model, "response_cost": 10000, **usage},
            }
        }

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        _url = os.getenv("LAGO_API_BASE")
        assert _url is not None and isinstance(
            _url, str
        ), "LAGO_API_BASE missing or not set correctly. LAGO_API_BASE={}".format(_url)
        if _url.endswith("/"):
            _url += "api/v1/events"
        else:
            _url += "/api/v1/events"

        api_key = os.getenv("LAGO_API_KEY")

        _data = self._common_logic(kwargs=kwargs, response_obj=response_obj)
        _headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(api_key),
        }

        try:
            response = self.sync_http_handler.post(
                url=_url,
                data=json.dumps(_data),
                headers=_headers,
            )

            response.raise_for_status()
        except Exception as e:
            if hasattr(response, "text"):
                litellm.print_verbose(f"\nError Message: {response.text}")
            raise e

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            _url = os.getenv("LAGO_API_BASE")
            assert _url is not None and isinstance(
                _url, str
            ), "LAGO_API_BASE missing or not set correctly. LAGO_API_BASE={}".format(
                _url
            )
            if _url.endswith("/"):
                _url += "api/v1/events"
            else:
                _url += "/api/v1/events"

            api_key = os.getenv("LAGO_API_KEY")

            _data = self._common_logic(kwargs=kwargs, response_obj=response_obj)
            _headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(api_key),
            }
        except Exception as e:
            raise e

        response: Optional[httpx.Response] = None
        try:
            response = await self.async_http_handler.post(
                url=_url,
                data=json.dumps(_data),
                headers=_headers,
            )

            response.raise_for_status()
        except Exception as e:
            if response is not None and hasattr(response, "text"):
                litellm.print_verbose(f"\nError Message: {response.text}")
            raise e

# What is this?
## Allocates dynamic tpm/rpm quota for a project based on current traffic

import sys
import traceback
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

import litellm
from litellm import ModelResponse, Router
from litellm._logging import verbose_proxy_logger
from litellm.caching import DualCache
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy._types import UserAPIKeyAuth
from litellm.types.router import ModelGroupInfo


class DynamicRateLimiterCache:
    """
    Thin wrapper on DualCache for this file.

    Track number of active projects calling a model.
    """

    def __init__(self, cache: DualCache) -> None:
        self.cache = cache
        self.ttl = 60  # 1 min ttl

    async def async_get_cache(self, model: str) -> Optional[int]:
        key_name = "{}".format(model)
        response = await self.cache.async_get_cache(key=key_name)
        return response

    async def async_increment_cache(self, model: str, value: int):
        key_name = "{}".format(model)
        await self.cache.async_increment_cache(key=key_name, value=value, ttl=self.ttl)


class _PROXY_DynamicRateLimitHandler(CustomLogger):

    # Class variables or attributes
    def __init__(self, internal_usage_cache: DualCache):
        self.internal_usage_cache = DynamicRateLimiterCache(cache=internal_usage_cache)

    def update_variables(self, llm_router: Router):
        self.llm_router = llm_router

    async def check_available_tpm(self, model: str) -> Optional[int]:
        """
        For a given model, get it's available tpm

        Returns
        - int: if number found
        - None: if not found
        """
        active_projects = await self.internal_usage_cache.async_get_cache(model=model)
        model_group_info: Optional[ModelGroupInfo] = (
            self.llm_router.get_model_group_info(model_group=model)
        )

        available_tpm: Optional[int] = None
        if model_group_info is not None and model_group_info.tpm is not None:
            if active_projects is not None:
                available_tpm = int(model_group_info.tpm / active_projects)
            else:
                available_tpm = model_group_info.tpm

        return available_tpm

    # async def check_key_in_limits(
    #     self,
    #     user_api_key_dict: UserAPIKeyAuth,
    #     cache: DualCache,
    #     data: dict,
    #     call_type: str,
    #     max_parallel_requests: int,
    #     tpm_limit: int,
    #     rpm_limit: int,
    #     request_count_api_key: str,
    # ):
    #     current = await self.internal_usage_cache.async_get_cache(
    #         key=request_count_api_key
    #     )  # {"current_requests": 1, "current_tpm": 1, "current_rpm": 10}
    #     if current is None:
    #         if max_parallel_requests == 0 or tpm_limit == 0 or rpm_limit == 0:
    #             # base case
    #             raise HTTPException(
    #                 status_code=429, detail="Max parallel request limit reached."
    #             )
    #         new_val = {
    #             "current_requests": 1,
    #             "current_tpm": 0,
    #             "current_rpm": 0,
    #         }
    #         await self.internal_usage_cache.async_set_cache(
    #             request_count_api_key, new_val
    #         )
    #     elif (
    #         int(current["current_requests"]) < max_parallel_requests
    #         and current["current_tpm"] < tpm_limit
    #         and current["current_rpm"] < rpm_limit
    #     ):
    #         # Increase count for this token
    #         new_val = {
    #             "current_requests": current["current_requests"] + 1,
    #             "current_tpm": current["current_tpm"],
    #             "current_rpm": current["current_rpm"],
    #         }
    #         await self.internal_usage_cache.async_set_cache(
    #             request_count_api_key, new_val
    #         )
    #     else:
    #         raise HTTPException(
    #             status_code=429,
    #             detail=f"LiteLLM Rate Limit Handler: Crossed TPM, RPM Limit. current rpm: {current['current_rpm']}, rpm limit: {rpm_limit}, current tpm: {current['current_tpm']}, tpm limit: {tpm_limit}",
    #         )

    # async def async_pre_call_hook(
    #     self,
    #     user_api_key_dict: UserAPIKeyAuth,
    #     cache: DualCache,
    #     data: dict,
    #     call_type: str,
    # ):
    #     self.print_verbose("Inside Dynamic Rate Limit Handler Pre-Call Hook")
    #     api_key = user_api_key_dict.api_key
    #     max_parallel_requests = user_api_key_dict.max_parallel_requests
    #     if max_parallel_requests is None:
    #         max_parallel_requests = sys.maxsize
    #     global_max_parallel_requests = data.get("metadata", {}).get(
    #         "global_max_parallel_requests", None
    #     )
    #     tpm_limit = getattr(user_api_key_dict, "tpm_limit", sys.maxsize)
    #     if tpm_limit is None:
    #         tpm_limit = sys.maxsize
    #     rpm_limit = getattr(user_api_key_dict, "rpm_limit", sys.maxsize)
    #     if rpm_limit is None:
    #         rpm_limit = sys.maxsize

    #     # ------------
    #     # Setup values
    #     # ------------

    #     if global_max_parallel_requests is not None:
    #         # get value from cache
    #         _key = "global_max_parallel_requests"
    #         current_global_requests = await self.internal_usage_cache.async_get_cache(
    #             key=_key, local_only=True
    #         )
    #         # check if below limit
    #         if current_global_requests is None:
    #             current_global_requests = 1
    #         # if above -> raise error
    #         if current_global_requests >= global_max_parallel_requests:
    #             raise HTTPException(
    #                 status_code=429, detail="Max parallel request limit reached."
    #             )
    #         # if below -> increment
    #         else:
    #             await self.internal_usage_cache.async_increment_cache(
    #                 key=_key, value=1, local_only=True
    #             )

    #     current_date = datetime.now().strftime("%Y-%m-%d")
    #     current_hour = datetime.now().strftime("%H")
    #     current_minute = datetime.now().strftime("%M")
    #     precise_minute = f"{current_date}-{current_hour}-{current_minute}"

    #     if api_key is not None:
    #         request_count_api_key = f"{api_key}::{precise_minute}::request_count"

    #         # CHECK IF REQUEST ALLOWED for key

    #         current = await self.internal_usage_cache.async_get_cache(
    #             key=request_count_api_key
    #         )  # {"current_requests": 1, "current_tpm": 1, "current_rpm": 10}
    #         self.print_verbose(f"current: {current}")
    #         if (
    #             max_parallel_requests == sys.maxsize
    #             and tpm_limit == sys.maxsize
    #             and rpm_limit == sys.maxsize
    #         ):
    #             pass
    #         elif max_parallel_requests == 0 or tpm_limit == 0 or rpm_limit == 0:
    #             raise HTTPException(
    #                 status_code=429, detail="Max parallel request limit reached."
    #             )
    #         elif current is None:
    #             new_val = {
    #                 "current_requests": 1,
    #                 "current_tpm": 0,
    #                 "current_rpm": 0,
    #             }
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val
    #             )
    #         elif (
    #             int(current["current_requests"]) < max_parallel_requests
    #             and current["current_tpm"] < tpm_limit
    #             and current["current_rpm"] < rpm_limit
    #         ):
    #             # Increase count for this token
    #             new_val = {
    #                 "current_requests": current["current_requests"] + 1,
    #                 "current_tpm": current["current_tpm"],
    #                 "current_rpm": current["current_rpm"],
    #             }
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val
    #             )
    #         else:
    #             raise HTTPException(
    #                 status_code=429, detail="Max parallel request limit reached."
    #             )

    #     # check if REQUEST ALLOWED for user_id
    #     user_id = user_api_key_dict.user_id
    #     if user_id is not None:
    #         _user_id_rate_limits = await self.internal_usage_cache.async_get_cache(
    #             key=user_id
    #         )
    #         # get user tpm/rpm limits
    #         if _user_id_rate_limits is not None and isinstance(
    #             _user_id_rate_limits, dict
    #         ):
    #             user_tpm_limit = _user_id_rate_limits.get("tpm_limit", None)
    #             user_rpm_limit = _user_id_rate_limits.get("rpm_limit", None)
    #             if user_tpm_limit is None:
    #                 user_tpm_limit = sys.maxsize
    #             if user_rpm_limit is None:
    #                 user_rpm_limit = sys.maxsize

    #             # now do the same tpm/rpm checks
    #             request_count_api_key = f"{user_id}::{precise_minute}::request_count"

    #             # print(f"Checking if {request_count_api_key} is allowed to make request for minute {precise_minute}")
    #             await self.check_key_in_limits(
    #                 user_api_key_dict=user_api_key_dict,
    #                 cache=cache,
    #                 data=data,
    #                 call_type=call_type,
    #                 max_parallel_requests=sys.maxsize,  # TODO: Support max parallel requests for a user
    #                 request_count_api_key=request_count_api_key,
    #                 tpm_limit=user_tpm_limit,
    #                 rpm_limit=user_rpm_limit,
    #             )

    #     # TEAM RATE LIMITS
    #     ## get team tpm/rpm limits
    #     team_id = user_api_key_dict.team_id
    #     if team_id is not None:
    #         team_tpm_limit = user_api_key_dict.team_tpm_limit
    #         team_rpm_limit = user_api_key_dict.team_rpm_limit

    #         if team_tpm_limit is None:
    #             team_tpm_limit = sys.maxsize
    #         if team_rpm_limit is None:
    #             team_rpm_limit = sys.maxsize

    #         # now do the same tpm/rpm checks
    #         request_count_api_key = f"{team_id}::{precise_minute}::request_count"

    #         # print(f"Checking if {request_count_api_key} is allowed to make request for minute {precise_minute}")
    #         await self.check_key_in_limits(
    #             user_api_key_dict=user_api_key_dict,
    #             cache=cache,
    #             data=data,
    #             call_type=call_type,
    #             max_parallel_requests=sys.maxsize,  # TODO: Support max parallel requests for a team
    #             request_count_api_key=request_count_api_key,
    #             tpm_limit=team_tpm_limit,
    #             rpm_limit=team_rpm_limit,
    #         )

    #     # End-User Rate Limits
    #     # Only enforce if user passed `user` to /chat, /completions, /embeddings
    #     if user_api_key_dict.end_user_id:
    #         end_user_tpm_limit = getattr(
    #             user_api_key_dict, "end_user_tpm_limit", sys.maxsize
    #         )
    #         end_user_rpm_limit = getattr(
    #             user_api_key_dict, "end_user_rpm_limit", sys.maxsize
    #         )

    #         if end_user_tpm_limit is None:
    #             end_user_tpm_limit = sys.maxsize
    #         if end_user_rpm_limit is None:
    #             end_user_rpm_limit = sys.maxsize

    #         # now do the same tpm/rpm checks
    #         request_count_api_key = (
    #             f"{user_api_key_dict.end_user_id}::{precise_minute}::request_count"
    #         )

    #         # print(f"Checking if {request_count_api_key} is allowed to make request for minute {precise_minute}")
    #         await self.check_key_in_limits(
    #             user_api_key_dict=user_api_key_dict,
    #             cache=cache,
    #             data=data,
    #             call_type=call_type,
    #             max_parallel_requests=sys.maxsize,  # TODO: Support max parallel requests for an End-User
    #             request_count_api_key=request_count_api_key,
    #             tpm_limit=end_user_tpm_limit,
    #             rpm_limit=end_user_rpm_limit,
    #         )

    #     return

    # async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
    #     try:
    #         self.print_verbose("INSIDE parallel request limiter ASYNC SUCCESS LOGGING")
    #         global_max_parallel_requests = kwargs["litellm_params"]["metadata"].get(
    #             "global_max_parallel_requests", None
    #         )
    #         user_api_key = kwargs["litellm_params"]["metadata"]["user_api_key"]
    #         user_api_key_user_id = kwargs["litellm_params"]["metadata"].get(
    #             "user_api_key_user_id", None
    #         )
    #         user_api_key_team_id = kwargs["litellm_params"]["metadata"].get(
    #             "user_api_key_team_id", None
    #         )
    #         user_api_key_end_user_id = kwargs.get("user")

    #         # ------------
    #         # Setup values
    #         # ------------

    #         if global_max_parallel_requests is not None:
    #             # get value from cache
    #             _key = "global_max_parallel_requests"
    #             # decrement
    #             await self.internal_usage_cache.async_increment_cache(
    #                 key=_key, value=-1, local_only=True
    #             )

    #         current_date = datetime.now().strftime("%Y-%m-%d")
    #         current_hour = datetime.now().strftime("%H")
    #         current_minute = datetime.now().strftime("%M")
    #         precise_minute = f"{current_date}-{current_hour}-{current_minute}"

    #         total_tokens = 0

    #         if isinstance(response_obj, ModelResponse):
    #             total_tokens = response_obj.usage.total_tokens

    #         # ------------
    #         # Update usage - API Key
    #         # ------------

    #         if user_api_key is not None:
    #             request_count_api_key = (
    #                 f"{user_api_key}::{precise_minute}::request_count"
    #             )

    #             current = await self.internal_usage_cache.async_get_cache(
    #                 key=request_count_api_key
    #             ) or {
    #                 "current_requests": 1,
    #                 "current_tpm": total_tokens,
    #                 "current_rpm": 1,
    #             }

    #             new_val = {
    #                 "current_requests": max(current["current_requests"] - 1, 0),
    #                 "current_tpm": current["current_tpm"] + total_tokens,
    #                 "current_rpm": current["current_rpm"] + 1,
    #             }

    #             self.print_verbose(
    #                 f"updated_value in success call: {new_val}, precise_minute: {precise_minute}"
    #             )
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val, ttl=60
    #             )  # store in cache for 1 min.

    #         # ------------
    #         # Update usage - User
    #         # ------------
    #         if user_api_key_user_id is not None:
    #             total_tokens = 0

    #             if isinstance(response_obj, ModelResponse):
    #                 total_tokens = response_obj.usage.total_tokens

    #             request_count_api_key = (
    #                 f"{user_api_key_user_id}::{precise_minute}::request_count"
    #             )

    #             current = await self.internal_usage_cache.async_get_cache(
    #                 key=request_count_api_key
    #             ) or {
    #                 "current_requests": 1,
    #                 "current_tpm": total_tokens,
    #                 "current_rpm": 1,
    #             }

    #             new_val = {
    #                 "current_requests": max(current["current_requests"] - 1, 0),
    #                 "current_tpm": current["current_tpm"] + total_tokens,
    #                 "current_rpm": current["current_rpm"] + 1,
    #             }

    #             self.print_verbose(
    #                 f"updated_value in success call: {new_val}, precise_minute: {precise_minute}"
    #             )
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val, ttl=60
    #             )  # store in cache for 1 min.

    #         # ------------
    #         # Update usage - Team
    #         # ------------
    #         if user_api_key_team_id is not None:
    #             total_tokens = 0

    #             if isinstance(response_obj, ModelResponse):
    #                 total_tokens = response_obj.usage.total_tokens

    #             request_count_api_key = (
    #                 f"{user_api_key_team_id}::{precise_minute}::request_count"
    #             )

    #             current = await self.internal_usage_cache.async_get_cache(
    #                 key=request_count_api_key
    #             ) or {
    #                 "current_requests": 1,
    #                 "current_tpm": total_tokens,
    #                 "current_rpm": 1,
    #             }

    #             new_val = {
    #                 "current_requests": max(current["current_requests"] - 1, 0),
    #                 "current_tpm": current["current_tpm"] + total_tokens,
    #                 "current_rpm": current["current_rpm"] + 1,
    #             }

    #             self.print_verbose(
    #                 f"updated_value in success call: {new_val}, precise_minute: {precise_minute}"
    #             )
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val, ttl=60
    #             )  # store in cache for 1 min.

    #         # ------------
    #         # Update usage - End User
    #         # ------------
    #         if user_api_key_end_user_id is not None:
    #             total_tokens = 0

    #             if isinstance(response_obj, ModelResponse):
    #                 total_tokens = response_obj.usage.total_tokens

    #             request_count_api_key = (
    #                 f"{user_api_key_end_user_id}::{precise_minute}::request_count"
    #             )

    #             current = await self.internal_usage_cache.async_get_cache(
    #                 key=request_count_api_key
    #             ) or {
    #                 "current_requests": 1,
    #                 "current_tpm": total_tokens,
    #                 "current_rpm": 1,
    #             }

    #             new_val = {
    #                 "current_requests": max(current["current_requests"] - 1, 0),
    #                 "current_tpm": current["current_tpm"] + total_tokens,
    #                 "current_rpm": current["current_rpm"] + 1,
    #             }

    #             self.print_verbose(
    #                 f"updated_value in success call: {new_val}, precise_minute: {precise_minute}"
    #             )
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val, ttl=60
    #             )  # store in cache for 1 min.

    #     except Exception as e:
    #         self.print_verbose(e)  # noqa

    # async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
    #     try:
    #         self.print_verbose(f"Inside Max Parallel Request Failure Hook")
    #         global_max_parallel_requests = kwargs["litellm_params"]["metadata"].get(
    #             "global_max_parallel_requests", None
    #         )
    #         user_api_key = (
    #             kwargs["litellm_params"].get("metadata", {}).get("user_api_key", None)
    #         )
    #         self.print_verbose(f"user_api_key: {user_api_key}")
    #         if user_api_key is None:
    #             return

    #         ## decrement call count if call failed
    #         if "Max parallel request limit reached" in str(kwargs["exception"]):
    #             pass  # ignore failed calls due to max limit being reached
    #         else:
    #             # ------------
    #             # Setup values
    #             # ------------

    #             if global_max_parallel_requests is not None:
    #                 # get value from cache
    #                 _key = "global_max_parallel_requests"
    #                 current_global_requests = (
    #                     await self.internal_usage_cache.async_get_cache(
    #                         key=_key, local_only=True
    #                     )
    #                 )
    #                 # decrement
    #                 await self.internal_usage_cache.async_increment_cache(
    #                     key=_key, value=-1, local_only=True
    #                 )

    #             current_date = datetime.now().strftime("%Y-%m-%d")
    #             current_hour = datetime.now().strftime("%H")
    #             current_minute = datetime.now().strftime("%M")
    #             precise_minute = f"{current_date}-{current_hour}-{current_minute}"

    #             request_count_api_key = (
    #                 f"{user_api_key}::{precise_minute}::request_count"
    #             )

    #             # ------------
    #             # Update usage
    #             # ------------
    #             current = await self.internal_usage_cache.async_get_cache(
    #                 key=request_count_api_key
    #             ) or {
    #                 "current_requests": 1,
    #                 "current_tpm": 0,
    #                 "current_rpm": 0,
    #             }

    #             new_val = {
    #                 "current_requests": max(current["current_requests"] - 1, 0),
    #                 "current_tpm": current["current_tpm"],
    #                 "current_rpm": current["current_rpm"],
    #             }

    #             self.print_verbose(f"updated_value in failure call: {new_val}")
    #             await self.internal_usage_cache.async_set_cache(
    #                 request_count_api_key, new_val, ttl=60
    #             )  # save in cache for up to 1 min.
    #     except Exception as e:
    #         verbose_proxy_logger.info(
    #             f"Inside Parallel Request Limiter: An exception occurred - {str(e)}."
    #         )

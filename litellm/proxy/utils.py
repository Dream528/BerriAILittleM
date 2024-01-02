from typing import Optional, List, Any, Literal
import os, subprocess, hashlib, importlib, asyncio, copy, json, aiohttp
import litellm, backoff
from litellm.proxy._types import UserAPIKeyAuth
from litellm.caching import DualCache
from litellm.proxy.hooks.parallel_request_limiter import MaxParallelRequestsHandler
from litellm.proxy.hooks.max_budget_limiter import MaxBudgetLimiter
from litellm.integrations.custom_logger import CustomLogger
from fastapi import HTTPException, status


def print_verbose(print_statement):
    if litellm.set_verbose:
        print(f"LiteLLM Proxy: {print_statement}")  # noqa


### LOGGING ###
class ProxyLogging:
    """
    Logging/Custom Handlers for proxy.

    Implemented mainly to:
    - log successful/failed db read/writes
    - support the max parallel request integration
    """

    def __init__(self, user_api_key_cache: DualCache):
        ## INITIALIZE  LITELLM CALLBACKS ##
        self.call_details: dict = {}
        self.call_details["user_api_key_cache"] = user_api_key_cache
        self.max_parallel_request_limiter = MaxParallelRequestsHandler()
        self.max_budget_limiter = MaxBudgetLimiter()
        pass

    def update_values(self, alerting: Optional[List]):
        self.alerting = alerting

    def _init_litellm_callbacks(self):
        print_verbose(f"INITIALIZING LITELLM CALLBACKS!")
        litellm.callbacks.append(self.max_parallel_request_limiter)
        litellm.callbacks.append(self.max_budget_limiter)
        for callback in litellm.callbacks:
            if callback not in litellm.input_callback:
                litellm.input_callback.append(callback)
            if callback not in litellm.success_callback:
                litellm.success_callback.append(callback)
            if callback not in litellm.failure_callback:
                litellm.failure_callback.append(callback)
            if callback not in litellm._async_success_callback:
                litellm._async_success_callback.append(callback)
            if callback not in litellm._async_failure_callback:
                litellm._async_failure_callback.append(callback)

        if (
            len(litellm.input_callback) > 0
            or len(litellm.success_callback) > 0
            or len(litellm.failure_callback) > 0
        ):
            callback_list = list(
                set(
                    litellm.input_callback
                    + litellm.success_callback
                    + litellm.failure_callback
                )
            )
            litellm.utils.set_callbacks(callback_list=callback_list)

    async def pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        data: dict,
        call_type: Literal["completion", "embeddings"],
    ):
        """
        Allows users to modify/reject the incoming request to the proxy, without having to deal with parsing Request body.

        Covers:
        1. /chat/completions
        2. /embeddings
        3. /image/generation
        """
        ### ALERTING ###
        asyncio.create_task(self.response_taking_too_long())

        try:
            for callback in litellm.callbacks:
                if isinstance(callback, CustomLogger) and "async_pre_call_hook" in vars(
                    callback.__class__
                ):
                    response = await callback.async_pre_call_hook(
                        user_api_key_dict=user_api_key_dict,
                        cache=self.call_details["user_api_key_cache"],
                        data=data,
                        call_type=call_type,
                    )
                    if response is not None:
                        data = response

            print_verbose(f"final data being sent to {call_type} call: {data}")
            return data
        except Exception as e:
            raise e

    async def success_handler(self, *args, **kwargs):
        """
        Log successful db read/writes
        """
        pass

    async def response_taking_too_long(self):
        # Simulate a long-running operation that could take more than 5 minutes
        await asyncio.sleep(
            300
        )  # Set it to 5 minutes - i'd imagine this might be different for streaming, non-streaming, non-completion (embedding + img) requests
        await self.alerting_handler(message="Requests are hanging", level="Medium")

    async def alerting_handler(
        self, message: str, level: Literal["Low", "Medium", "High"]
    ):
        """
        Alerting based on thresholds: - https://github.com/BerriAI/litellm/issues/1298

        - Responses taking too long
        - Requests are hanging
        - Calls are failing
        - DB Read/Writes are failing

        Parameters:
            level: str - Low|Medium|High - if calls might fail (Medium) or are failing (High); Currently, no alerts would be 'Low'.
            message: str - what is the alert about
        """
        formatted_message = f"Level: {level}\n\nMessage: {message}"
        if self.alerting is None:
            return

        for client in self.alerting:
            if client == "slack":
                slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", None)
                if slack_webhook_url is None:
                    raise Exception("Missing SLACK_WEBHOOK_URL from environment")
                payload = {"text": formatted_message}
                headers = {"Content-type": "application/json"}
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        slack_webhook_url, json=payload, headers=headers
                    ) as response:
                        if response.status == 200:
                            pass
            elif client == "sentry":
                if litellm.utils.sentry_sdk_instance is not None:
                    litellm.utils.sentry_sdk_instance.capture_message(formatted_message)
                else:
                    raise Exception("Missing SENTRY_DSN from environment")

    async def failure_handler(self, original_exception):
        """
        Log failed db read/writes

        Currently only logs exceptions to sentry
        """
        ### ALERTING ###
        if isinstance(original_exception, HTTPException):
            error_message = original_exception.detail
        else:
            error_message = str(original_exception)
        asyncio.create_task(
            self.alerting_handler(
                message=f"DB read/write call failed: {error_message}",
                level="High",
            )
        )

        if litellm.utils.capture_exception:
            litellm.utils.capture_exception(error=original_exception)

    async def post_call_failure_hook(
        self, original_exception: Exception, user_api_key_dict: UserAPIKeyAuth
    ):
        """
        Allows users to raise custom exceptions/log when a call fails, without having to deal with parsing Request body.

        Covers:
        1. /chat/completions
        2. /embeddings
        3. /image/generation
        """

        ### ALERTING ###
        asyncio.create_task(
            self.alerting_handler(
                message=f"LLM API call failed: {str(original_exception)}", level="High"
            )
        )

        for callback in litellm.callbacks:
            try:
                if isinstance(callback, CustomLogger):
                    await callback.async_post_call_failure_hook(
                        user_api_key_dict=user_api_key_dict,
                        original_exception=original_exception,
                    )
            except Exception as e:
                raise e
        return


### DB CONNECTOR ###
# Define the retry decorator with backoff strategy
# Function to be called whenever a retry is about to happen
def on_backoff(details):
    # The 'tries' key in the details dictionary contains the number of completed tries
    print_verbose(f"Backing off... this was attempt #{details['tries']}")


class PrismaClient:
    def __init__(self, database_url: str, proxy_logging_obj: ProxyLogging):
        print_verbose(
            "LiteLLM: DATABASE_URL Set in config, trying to 'pip install prisma'"
        )
        ## init logging object
        self.proxy_logging_obj = proxy_logging_obj

        os.environ["DATABASE_URL"] = database_url
        # Save the current working directory
        original_dir = os.getcwd()
        # set the working directory to where this script is
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        try:
            subprocess.run(["prisma", "generate"])
            subprocess.run(
                ["prisma", "db", "push", "--accept-data-loss"]
            )  # this looks like a weird edge case when prisma just wont start on render. we need to have the --accept-data-loss
        finally:
            os.chdir(original_dir)
        # Now you can import the Prisma Client
        from prisma import Client  # type: ignore

        self.db = Client()  # Client to connect to Prisma db

    def hash_token(self, token: str):
        # Hash the string using SHA-256
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        return hashed_token

    def jsonify_object(self, data: dict) -> dict:
        db_data = copy.deepcopy(data)

        for k, v in db_data.items():
            if isinstance(v, dict):
                db_data[k] = json.dumps(v)
        return db_data

    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def get_generic_data(
        self,
        key: str,
        value: Any,
        db: Literal["users", "keys"],
    ):
        """
        Generic implementation of get data
        """
        try:
            if db == "users":
                response = await self.db.litellm_usertable.find_first(
                    where={key: value}  # type: ignore
                )
            elif db == "keys":
                response = await self.db.litellm_verificationtoken.find_first(  # type: ignore
                    where={key: value}  # type: ignore
                )
            return response
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            raise e

    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def get_data(
        self,
        token: Optional[str] = None,
        expires: Optional[Any] = None,
        user_id: Optional[str] = None,
    ):
        try:
            response = None
            if token is not None:
                # check if plain text or hash
                hashed_token = token
                if token.startswith("sk-"):
                    hashed_token = self.hash_token(token=token)
                response = await self.db.litellm_verificationtoken.find_unique(
                    where={"token": hashed_token}
                )
                if response:
                    # Token exists, now check expiration.
                    if response.expires is not None and expires is not None:
                        if response.expires >= expires:
                            # Token exists and is not expired.
                            return response
                        else:
                            # Token exists but is expired.
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="expired user key",
                            )
                    return response
                else:
                    # Token does not exist.
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="invalid user key",
                    )
            elif user_id is not None:
                response = await self.db.litellm_usertable.find_unique(  # type: ignore
                    where={
                        "user_id": user_id,
                    }
                )
                return response
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            raise e

    # Define a retrying strategy with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def insert_data(self, data: dict):
        """
        Add a key to the database. If it already exists, do nothing.
        """
        try:
            token = data["token"]
            hashed_token = self.hash_token(token=token)
            db_data = self.jsonify_object(data=data)
            db_data["token"] = hashed_token
            max_budget = db_data.pop("max_budget", None)
            user_email = db_data.pop("user_email", None)
            new_verification_token = await self.db.litellm_verificationtoken.upsert(  # type: ignore
                where={
                    "token": hashed_token,
                },
                data={
                    "create": {**db_data},  # type: ignore
                    "update": {},  # don't do anything if it already exists
                },
            )

            new_user_row = await self.db.litellm_usertable.upsert(
                where={"user_id": data["user_id"]},
                data={
                    "create": {
                        "user_id": data["user_id"],
                        "max_budget": max_budget,
                        "user_email": user_email,
                    },
                    "update": {},  # don't do anything if it already exists
                },
            )
            return new_verification_token
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            raise e

    # Define a retrying strategy with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def update_data(
        self,
        token: Optional[str] = None,
        data: dict = {},
        user_id: Optional[str] = None,
    ):
        """
        Update existing data
        """
        try:
            db_data = self.jsonify_object(data=data)
            if token is not None:
                print_verbose(f"token: {token}")
                # check if plain text or hash
                if token.startswith("sk-"):
                    token = self.hash_token(token=token)
                db_data["token"] = token
                response = await self.db.litellm_verificationtoken.update(
                    where={"token": token},  # type: ignore
                    data={**db_data},  # type: ignore
                )
                print_verbose("\033[91m" + f"DB write succeeded {response}" + "\033[0m")
                return {"token": token, "data": db_data}
            elif user_id is not None:
                """
                If data['spend'] + data['user'], update the user table with spend info as well
                """
                update_user_row = await self.db.litellm_usertable.update(
                    where={"user_id": user_id},  # type: ignore
                    data={**db_data},  # type: ignore
                )
                return {"user_id": user_id, "data": db_data}
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            print_verbose("\033[91m" + f"DB write failed: {e}" + "\033[0m")
            raise e

    # Define a retrying strategy with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def delete_data(self, tokens: List):
        """
        Allow user to delete a key(s)
        """
        try:
            hashed_tokens = [self.hash_token(token=token) for token in tokens]
            await self.db.litellm_verificationtoken.delete_many(
                where={"token": {"in": hashed_tokens}}
            )
            return {"deleted_keys": tokens}
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            raise e

    # Define a retrying strategy with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def connect(self):
        try:
            await self.db.connect()
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            raise e

    # Define a retrying strategy with exponential backoff
    @backoff.on_exception(
        backoff.expo,
        Exception,  # base exception to catch for the backoff
        max_tries=3,  # maximum number of retries
        max_time=10,  # maximum total time to retry for
        on_backoff=on_backoff,  # specifying the function to call on backoff
    )
    async def disconnect(self):
        try:
            await self.db.disconnect()
        except Exception as e:
            asyncio.create_task(
                self.proxy_logging_obj.failure_handler(original_exception=e)
            )
            raise e


### CUSTOM FILE ###
def get_instance_fn(value: str, config_file_path: Optional[str] = None) -> Any:
    try:
        print_verbose(f"value: {value}")
        # Split the path by dots to separate module from instance
        parts = value.split(".")

        # The module path is all but the last part, and the instance_name is the last part
        module_name = ".".join(parts[:-1])
        instance_name = parts[-1]

        # If config_file_path is provided, use it to determine the module spec and load the module
        if config_file_path is not None:
            directory = os.path.dirname(config_file_path)
            module_file_path = os.path.join(directory, *module_name.split("."))
            module_file_path += ".py"

            spec = importlib.util.spec_from_file_location(module_name, module_file_path)
            if spec is None:
                raise ImportError(
                    f"Could not find a module specification for {module_file_path}"
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
        else:
            # Dynamically import the module
            module = importlib.import_module(module_name)

        # Get the instance from the module
        instance = getattr(module, instance_name)

        return instance
    except ImportError as e:
        # Re-raise the exception with a user-friendly message
        raise ImportError(f"Could not import {instance_name} from {module_name}") from e
    except Exception as e:
        raise e


### HELPER FUNCTIONS ###
async def _cache_user_row(user_id: str, cache: DualCache, db: PrismaClient):
    """
    Check if a user_id exists in cache,
    if not retrieve it.
    """
    cache_key = f"{user_id}_user_api_key_user_id"
    response = cache.get_cache(key=cache_key)
    if response is None:  # Cache miss
        user_row = await db.get_data(user_id=user_id)
        cache_value = user_row.model_dump_json()
        cache.set_cache(
            key=cache_key, value=cache_value, ttl=600
        )  # store for 10 minutes
    return

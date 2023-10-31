import sys
import os
import io

sys.path.insert(0, os.path.abspath('../..'))

from litellm import completion
import litellm

litellm.failure_callback = ["sentry"]

import time

def test_exception_tracking():
    print('expect this to fail and log to sentry')
    litellm.set_verbose=True
    old_api_key = os.environ["OPENAI_API_KEY"]
    os.environ["OPENAI_API_KEY"] = "ss"
    try:
        response = completion(model="gpt-3.5-turbo",
                              messages=[{
                                  "role": "user",
                                  "content": "Hi 👋 - i'm claude"
                              }],
                              max_tokens=10,
                              temperature=0.2
                              )
        print(response)
        os.environ["OPENAI_API_KEY"]  = old_api_key
    except Exception as e:
        print("got_exception")
        print(e)
    os.environ["OPENAI_API_KEY"]  = old_api_key

test_exception_tracking()






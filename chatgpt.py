import time
import openai
from colorama import Fore
from config import cfg


def create_chat_completion(messages, model=cfg.fast_llm_model, temperature=cfg.temperature, max_tokens=None) -> str:
    """Create a chat completion using the OpenAI API"""
    response = None
    num_retries = 5
    for attempt in range(num_retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            break
        except openai.error.RateLimitError:
            if cfg.debug_mode:
                print(Fore.RED + "Error: ", "API Rate Limit Reached. Waiting 20 seconds..." + Fore.RESET)
            time.sleep(20)
        except openai.error.APIError as e:
            if e.http_status == 502:
                if cfg.debug_mode:
                    print(Fore.RED + "Error: ", "API Bad gateway. Waiting 20 seconds..." + Fore.RESET)
                time.sleep(20)
            else:
                raise
            if attempt == num_retries - 1:
                raise
        except openai.error.InvalidRequestError:
            raise

    if response is None:
        raise RuntimeError("Failed to get response after 5 retries")

    return response.choices[0].message["content"]

from config import Config
import ast

cfg = Config()

from chatgpt import create_chat_completion


# This is a magic function that can do anything with no-code. See
# https://github.com/Torantulino/AI-Functions for more info.
def call_ai_function(function, args, description, model=None):
    """Call an AI function"""
    if model is None:
        model = cfg.smart_llm_model
    # For each arg, if any are None, convert to "None":
    args = [str(arg) if arg is not None else "None" for arg in args]
    # parse args to comma separated string
    args = ", ".join(args)
    messages = [
        {
            "role": "system",
            "content": f"You are now the following python function: ```# {description}\n{function}```\n\nOnly respond with your `return` value. Do not include any other explanatory text in your response.",
        },
        {"role": "user", "content": args},
    ]
    # print(messages[0]["content"])
    # print(messages[1]["content"])
    # print(args)
    response = create_chat_completion(
        model=model, messages=messages, temperature=0
    )

    return response


def populate_sql_statement(sql_str: str, previous_sql_results: list[list[dict]]) -> list[str]:
    # Try to fix the SQL using GPT:
    function_string = "def populate_sql_statement(sql_str: str, previous_sql_results: list[list[dict]]) -> list[str]:"
    args = [f"'''{sql_str}'''", f"'''{previous_sql_results}'''"]
    description_string = "Find useful information in the results of the previous sql statement, and replace <> with the corresponding information."

    result_string = call_ai_function(
        function_string, args, description_string, model=cfg.fast_llm_model
    )
    # print("chatgpt", result_string)
    brace_index = result_string.index("[")
    result_string = result_string[brace_index:]
    last_brace_index = result_string.rindex("]")
    result_string = result_string[:last_brace_index + 1]
    # print(result_string)
    list_of_str = ast.literal_eval(result_string)
    return list_of_str


if __name__ == '__main__':
    previous_sql_results = [[{"sale_id": 3}],
                            [{"fruit_id": 2, "quantity_sold": 20}, {"fruit_id": 3, "quantity_sold": 20}]]
    sql_str = "SELECT fruit_id, quantity_sold FROM sale_items WHERE <sale_id>;"
    #     sql_str = """UPDATE fruits
    # SET stock_quantity = stock_quantity + <quantity_sold>
    # WHERE fruit_id = <fruit_id>;"""

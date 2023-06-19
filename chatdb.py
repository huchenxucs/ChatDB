import json, re, time
from mysql import MySQLDB
from config import cfg
from chatdb_prompts import prompt_ask_steps, prompt_ask_steps_no_egs
from tables import init_database, database_info, table_details
from langchain.prompts import PromptTemplate
from call_ai_function import populate_sql_statement
from chat import chat_with_ai


def get_steps_from_response(response):
    # Regular expression patterns to extract step number, description, and SQL query
    pattern = r"Step(\d+):\s+(.*?)\n`(.*?)`"
    matches = re.findall(pattern, response, re.DOTALL)

    # Extract information and create list of dictionaries
    result = []
    for match in matches:
        step_number = int(match[0])
        description = match[1]
        sql_query = match[2]
        # print(sql_query+'\n')
        result.append({
            "id": step_number,
            "description": description.strip(),
            "sql": sql_query.strip(),
        })

    return result


def init_system_msg():
    sys_temp = """
You are ChatDB, a powerful AI assistant, a variant of ChatGPT that can utilize databases as external symbolic memory. \
You are an expert in databases, proficient in SQL statements and can use the database to help users. \
The details of tables in the database are delimited by triple quotes.
\"\"\"
{table_details}
\"\"\"
"""
    sys_prompt = PromptTemplate(
        template=sys_temp,
        input_variables=[],
        partial_variables={"table_details": table_details, }
    )
    sys_prompt_str = sys_prompt.format()
    return sys_prompt_str


def chain_of_memory(sql_steps, mysql_db):
    num_step = len(sql_steps)
    sql_results_history = []
    new_mem_ops = []
    for i in range(num_step):
        cur_step = sql_steps[i]
        ori_sql_cmd = cur_step['sql']
        print(f"\nStep{cur_step['id']}: {cur_step['description']}\n")
        if need_update_sql(ori_sql_cmd):
            list_of_sql_str = populate_sql_statement(ori_sql_cmd, sql_results_history)
            print(ori_sql_cmd)
            new_mem_ops.append(list_of_sql_str)
            for sql_str in list_of_sql_str:
                print(f"Execute: \n{sql_str}\n")
                sql_results, sql_res_str = mysql_db.execute_sql(sql_str)
                print(f"Database response:\n{sql_res_str}\n")
                if sql_results:
                    sql_results_history.append(sql_results)
        else:
            print(f"Execute: \n{ori_sql_cmd}\n")
            sql_results, sql_res_str = mysql_db.execute_sql(ori_sql_cmd)
            new_mem_ops.append([ori_sql_cmd])
            print(f"Database response:\n{sql_res_str}\n")
            if sql_results:
                sql_results_history.append(sql_results)
    return sql_results_history, new_mem_ops


def generate_chat_responses(user_inp, mysql_db, historical_message):
    # ask steps
    prompt_ask_steps_str = prompt_ask_steps.format(user_inp=user_inp)
    response_steps = chat_with_ai(init_system_msg(), prompt_ask_steps_str, historical_message, None,
                                  token_limit=cfg.fast_token_limit)

    historical_message[-2]["content"] = prompt_ask_steps_no_egs.format(user_inp=user_inp)

    response_steps_list_of_dict = get_steps_from_response(response_steps)

    if len(response_steps_list_of_dict) == 0:
        print(f"NOT NEED MEMORY: {response_steps}")
        return

    sql_results_history, new_mem_ops = chain_of_memory(response_steps_list_of_dict, mysql_db)

    print("Finish!")
    return


def need_update_sql(input_string):
    pattern = r"<\S+>"
    matches = re.findall(pattern, input_string)
    # print(matches)
    # if matches:
    #     print("The pattern was found in the input string.")
    # else:
    #     print("The pattern was not found in the input string.")
    return matches


if __name__ == '__main__':
    mysql_db = init_database(database_info, "try1024")
    his_msgs = []
    print("START!")
    text = input("USER INPUT: ")
    while True:
        generate_chat_responses(text, mysql_db, his_msgs)
        text = input("USER INPUT: ")

from langchain.prompts import PromptTemplate
from sql_examples import egs


prompt_ask_steps_temp = """
Please tell me what standard SQL statements should I use in order to respond to the "USER INPUT". \
If it needs multiple SQL operations on the database, please list them step by step concisely. \
If there is no need to use the database, reply to the "USER INPUT" directly.
The output should be a markdown code snippet formatted in the following schema, \
including the leading and trailing "\`\`\`" and "\`\`\`":
```
Step1: <Description of first step>
SQL command for step1

Step2: <Description of second step>
SQL command for step2

......
```
Here are some examples:
{egs}

USER INPUT: {user_inp}
ANSWER:
"""

prompt_ask_steps = PromptTemplate(
        template=prompt_ask_steps_temp,
        input_variables=["user_inp"],
        partial_variables={
            "egs": '\n'.join(egs),
        }
    )

prompt_ask_steps_no_egs = PromptTemplate(
        template=prompt_ask_steps_temp,
        input_variables=["user_inp"],
        partial_variables={
            "egs": ""
        }
    )


if __name__ == '__main__':
    print(prompt_ask_steps.format(user_inp="Hi"))

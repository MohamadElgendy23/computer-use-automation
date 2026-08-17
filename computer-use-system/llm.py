import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class LLMDecisionMaker:
    def decide(self, observation, task):
        prompt = f"""
You are a computer-use agent.

Your job is to look at the current browser state and decide
what action should be taken next.

CURRENT PAGE:
{observation["page_text"]}

INTERACTIVE ELEMENTS:
{observation["elements"]}

TASK:
Member ID: {task.member_id}
Account Type: {task.account_type}
Initial Deposit: {task.initial_deposit}

Return a short description of the next action.
"""

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        return response.output_text


if __name__ == "__main__":
    test_observation = {
        "page_text": "Bank Operations Portal\nUsername:\nPassword:\nLogin",
        "elements": [
            {
                "tag": "INPUT",
                "id": "username",
                "name": "username",
                "type": "text",
            },
            {
                "tag": "INPUT",
                "id": "password",
                "name": "password",
                "type": "password",
            },
            {
                "tag": "BUTTON",
                "id": None,
                "name": None,
                "type": "submit",
            },
        ],
    }

    class TestTask:
        member_id = "12345"
        account_type = "savings"
        initial_deposit = "500"

    decision_maker = LLMDecisionMaker()

    decision = decision_maker.decide(
        test_observation,
        TestTask(),
    )

    print("REAL LLM RESPONSE:")
    print(decision)

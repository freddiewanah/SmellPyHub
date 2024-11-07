import openai
import json




openai.api_key = ''

test_smell = "AssertRoulette"  # replace with the actual test smell
test_code = "your test code here"  # replace with the actual test code

refactor_keys = json.load(open('smells/refactorKeys.json', 'r'))


def refactor_test_smell(test_smell, test_code):

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a senior Python developer."
            },
            {
                "role": "user",
                "content": f"I have a piece of test code that has the '{test_smell}' smell. "
                           f"The definition of this test smell is as follows:\n{refactor_keys[test_smell]['Definition']}\n"
                           f"Here are steps to refactor this smell:\n{refactor_keys[test_smell]['Steps']}\n"
                           f"Here is the code:\n\n{test_code}\n\nCan you help me refactor it to avoid this smell?"
                           f"\nPlease quote the code with three single quotes."
            }
        ]
    )


    return response.choices[0].message['content']


if __name__ == '__main__':
    with open('testFile.py', 'r') as f:
        test_code = f.read()

    response = refactor_test_smell('EmptyTest', test_code)

    # read the code from the response
    refactor_code = response.split('\n\n```')[1].split('```\n\n')[0]
    print(refactor_code)
import os
import openai
import asyncio

max_blocks = 50

language = os.getenv('TARGET_LANGUAGE')
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_lines():
    with open("input.srt", "r") as file:
        lines = file.readlines()
    return lines

def get_prompt(language, text):
    with open("prompt.txt", "r") as file:
        prompt = file.read()
    prompt = prompt.replace("{language}", language)
    prompt = prompt.replace("{text}", text)
    return prompt

async def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

async def translate(language, number, total, block):
    print(f"""Start #{number} of {total}...""")

    result = await get_completion(block)

    # Remove triple backticks from the result.
    result = result.replace("```\n", "")
    result = result.replace("```", "")

    # Make sure the result has the empty line at the end.
    result = result.rstrip().lstrip()
    result += "\n\n"

    print(f"""Finish #{number} of {total}...""")

    return result

async def main():
    blocks = []
    current_number_of_blocks = 0
    text = ""

    lines = get_lines()

    for line in lines:
        text += line
        if len(line.rstrip()) == 0 and len(text) > 0:
            current_number_of_blocks += 1
            if current_number_of_blocks >= max_blocks:
                blocks += [get_prompt(language, text)]
                current_number_of_blocks = 0
                text = ""
    if len(text) > 0:
        blocks += [get_prompt(language, text)]

    tasks = [translate(language, index + 1, len(blocks), block) for index, block in enumerate(blocks)]
    result = await asyncio.gather(*tasks)

    with open("output.srt", "w") as file:
        for line in result:
            file.write(line)

asyncio.run(main())

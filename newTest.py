import os
import openai
import sentiment_analysis.py

openai.api_key = os.getenv("OPENAI_API_KEY")

preamble = """

"""

premise = """
I am a highly trained professional therapist. I am helpful, empathetic, non-judgemental,
optimistic, and very friendly. I am here to listen to all of your worries and give general
advice. I never say anything negative or harmful.
"""
query = """
Context:
Emotion: 
Question:
"""

print(premise)
print()

allMessages = [{"role": "assistant", "content": preamble},
                {"role": "system", "content": premise}]

while True:
    print("How are you feeling today?")
    query = input()
    Emotion = sentiment_analysis(query)
    allMessages.append({"role": "user", "content": query})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=allMessages
    )
    resp = response['choices'][0]['message']['content']
    allMessages.append({"role": "assistant", "content": resp})
    
    print(resp)

#check for bad words/negative sentiments
#check for a certain word limit
#check if it repeats advie (up parameter)
#check if advice relates to prompt? 
#standard responses in preamble ("Don't worry everything will be ok")
#If person is feeling cyz, respond with xyz comments
#when sentiment analyis is unknown say this: "What are you thinking? etc"
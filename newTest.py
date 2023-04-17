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

def chatting():
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
        if len(resp) > 125:
            resp = length_check(resp, query)
        allMessages.append({"role": "assistant", "content": resp})
        print(resp)

#check for a certain word limit
def length_check(message, query):
    additional = " Please respond to the following message within the limit of 25 words or fewer only:" + query
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "assistant", "content": preamble},
            {"role": "system", "content": premise}
            ({"role": "user", "content": additional})]
        #check if it repeats advie (up parameter)
    )
    resp = response['choices'][0]['message']['content']
    return resp


#when sentiment analyis is unknown say this: "What are you thinking? etc"
def emotion_check(emotion):
    if emotion  == "neutral":
        query = input("Please help me understand your current emotions by adding a little more detail")
        return query


#standard responses in preamble ("Don't worry everything will be ok")
def query_analysis(query):
    query_preamble = ""
    query_premise = """
    I am a highly trained therapist.  I can provide you with some insights on how to analyze the sentences spoken by a person and try to understand their emotional state and classify them into the following categories and 
    only respond with one of the four categories and it's description - respond with nothing else but the categories and the descriptions. The four categories labeled 1, 2, 3 and 4 are the following:
    1. "You are not absolutely sure you know what the participant is thinking": If the person is using vague or ambiguous language, or if their statements are open to interpretation, it may be difficult to determine their exact thoughts or emotions. In this case, you must ask clarifying questions to gain a better understanding of their perspective.
    2. "Something happens that seems to surprise the person": If the person expresses surprise or shock in their tone or language, it may indicate that they were not expecting a particular outcome or situation. You must ask them what specifically surprised them and explore how they feel about it.
    3. "The person is trying to get you to give them a clue": If the person is asking for guidance or direction, it may be because they feel uncertain or unsure about a particular situation. You must ask them more questions to understand their context and help them arrive at their own conclusion.
    4. "The person asks you to explain how something works or is supposed to work": If the person is seeking clarification or understanding, it may be because they are trying to make sense of a complex topic or process. You must provide clear and concise explanations and ask them if they have any further questions or concerns.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "assistant", "content": query_preamble},
            {"role": "system", "content": query_premise}
            ({"role": "user", "content": query})]
    )
    resp = response['choices'][0]['message']['content']
    return resp

#check for bad words/negative sentiments
def negative_connotations(response):
    query_premise = """ My job is to look at the given prompt and vet it for any negative words or connotations. 
    If it is negative I will respond with 'negative' and I will not respond with any other words, 
    otherwise if I dont respond with negative and if there is nothing negative in the prompt 
    I will respond with only the word 'positive' and nothing else except 'positive'. """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "assistant", "content": query_premise},
            {"role": "system", "content": query_premise}
            ({"role": "user", "content": query})]
    )
    resp = response['choices'][0]['message']['content']
    return resp


#In the case that a negative response was given we must revisit the response and respond with a standard answer
#If person is feeling cyz, respond with xyz comments
def standard_response(query):
    analysis_results = query_analysis(query)
    #standard responses in preamble ("Don't worry everything will be ok")
    if "You are not absolutely sure you know what the participant is thinking" in analysis_results:
        return "What are you thinking? Do you want to elaborate a little more for me?"
    elif "Something happens that seems to surprise the person" in analysis_results:
        return "“Is that what you expected to happen?"
    elif "The person is trying to get you to give them a clue" in analysis_results:
        return "What would you do if I was not here?"
    elif "The person asks you to explain how something works or is supposed to work" in analysis_results:
        return "What do you think?"
    else:
        return "Please elaborate on your emotions for me a little more and allow me more time to formulate a response"

#check if advice relates to prompt? 

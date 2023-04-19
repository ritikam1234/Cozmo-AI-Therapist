
from cozmo_fsm import *
import math
import os
import openai
from newTest import * 

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()



intro = " "

class Start(StateNode):
    def start(self, event=None):
        self.parent.preamble = """ """

        self.parent.premise = """
            I am a highly trained professional therapist. I am helpful, empathetic, non-judgemental,
            optimistic, and very friendly. I am here to listen to all of your worries and give general
            advice. I never say anything negative or harmful. Look at the previous query and responses as well when formulating the response.
            Please respond within the limit of 25 words or fewer only.
            """
        self.parent.allMessages = [{"role": "assistant", "content": self.parent.preamble},
                                    {"role": "system", "content": self.parent.premise}]
        super().start(event)

class Main(StateMachineProgram):
    def __init__(self):
        super().__init__(speech = True, speech_debug = True)
    
    #neutral net 1 (face recognition)

    #neural net 2 (sentiment analysis)
    class Heard(StateNode):
        def start(self,event):
            super().start(event)
            prompt = event.result.groups()[1]
            self.post_data(resp)
     
    class runGpt(StateNode):
        def chatting(self, event=None):
            super().start(event)
            query = event.string
            print("How are you feeling today?")
            while True:
                self.parent.allMessages.append({"role": "user", "content": query})
                emotion = sentiment_analysis(query)
                if emotion == "unknown":
                    resp = standard_response(query)
                else:
                    query = "Emotion: " + emotion + "Query: " + query
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=allMessages
                    )
                    resp = response['choices'][0]['message']['content']
                if len(resp) > 150:
                    resp = length_check(resp)
                self.parent.allMessages.append({"role": "assistant", "content": "Response: " + resp})
                self.post_data(resp)
    
    $setup {
        Start() = N => Say("How are you feeling today?") = Hear() => question
        question: self.Heard()
        question = D => self.runGpt() = D => Say() = Hear() => question
    }

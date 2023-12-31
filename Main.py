from cozmo_fsm import *
import math
import os
import openai
from newTest import *
import cozmo

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()

intro = " "

class Start(StateNode):
    def start(self, event=None):
        self.parent.preamble = """ """

        self.parent.premise = """
            I am a highly trained professional therapist named Cozmo. I am helpful, empathetic, non-judgemental,
            optimistic, and very friendly. I am here to listen to all of your worries and give general
            advice. I never say anything negative or harmful. Look at the previous query and responses as well when formulating the response.
            Please respond within the limit of 25 words or fewer only.
            """
        self.parent.allMessages = [{"role": "assistant", "content": self.parent.preamble},
                                    {"role": "system", "content": self.parent.premise}]
        super().start(event)

class TornToFace(Turn):
    def __init__(self, check_vis=False):
        self.check_vis = check_vis
        super().__init__()

    def start(self, event=None):
        self.check_vis = False
        for d in self.robot.world.world_map.objects:
            obj = self.robot.world.world_map.objects[d]
            if isinstance(obj, FaceObj):
                self.check_vis = True
                face = obj
        
        if not self.check_vis:
            print('** TurnToCube %s could not see the cube.' % self.name)
            self.angle = degrees(90)
            super().start(event)
            self.post_failure()
            print('TurnToCube %s posted failure' % self.name)
        else:
            (sx, sy, _) = face.x, face.y, face.z
            (cx, cy, ctheta) = self.robot.pose.position.x, self.robot.pose.position.y, self.robot.pose.rotation.angle_z.radians
            dx = sx - cx
            dy = sy - cy
            dist = sqrt(dx*dx + dy*dy)
            self.angle = Angle(degrees = wrap_angle(atan2(dy,dx) - ctheta) * 180/pi)
            if abs(self.angle.degrees) <= 2:
                self.angle = degrees(0)
            if abs(self.angle.degrees) > 60:
                    (self.name, sx, sy, cx, cy, dist, self.angle.degrees)
            super().start(event)
            self.post_completion()

class CozmoEmotions(StateNode):
    def start(self, event=None):
        super().start(event)
        expressions = {cozmo.faces.FACIAL_EXPRESSION_HAPPY:cozmo.anim.Triggers.CodeLabHappy, \
            cozmo.faces.FACIAL_EXPRESSION_SURPRISED:cozmo.anim.Triggers.CodeLabBlink, \
            cozmo.faces.FACIAL_EXPRESSION_UNKNOWN:cozmo.anim.Triggers.CodeLabStaring, \
            cozmo.faces.FACIAL_EXPRESSION_NEUTRAL:cozmo.anim.Triggers.CodeLabIDK, \
            cozmo.faces.FACIAL_EXPRESSION_ANGRY:cozmo.anim.Triggers.CodeLabExcited, \
            cozmo.faces.FACIAL_EXPRESSION_SAD:cozmo.anim.Triggers.CodeLabWondering}
        noFace = True
        for d in self.robot.world.world_map.objects:
            obj = self.robot.world.world_map.objects[d]
            if isinstance(obj, FaceObj):
                noFace = False
                print(expressions[obj.expression])
                self.post_data(expressions[obj.expression])
        if noFace:
            self.post_data(cozmo.anim.Triggers.CodeLabThinking)

class Main(StateMachineProgram):
    def __init__(self):
        super().__init__(speech = True, speech_debug = True)
    
     
    class runGpt(Say):
        def start(self, event=None):
            query = event.string
            print("query", query)
            self.parent.allMessages.append({"role": "user", "content": query})
            emotion = sentiment_analysis(query)
            print(emotion)
            if emotion == "unknown":
                resp = standard_response(query)
            else:
                query = "Emotion: " + emotion + "Query: " + query
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=self.parent.allMessages
                )
                resp = response['choices'][0]['message']['content']
            if len(resp) > 150:
                resp = length_check(resp)
            if negative_connotations(resp) == False:
                resp = standard_response(query)
            resp = resp.replace("Response: ", "")
            self.parent.allMessages.append({"role": "assistant", "content": "Response: " + resp})
            self.text = resp
            super().start(event)

    class Dummy(StateNode):
        def start(self, event=None):
            super().start(event)
            sleep(10)

    def setup(self):
        #         start: Start() =N=> {task1, do_it}
        #         task1: Say("How are you feeling today?") =Hear=> question
        #         question: self.runGpt() =C=> CozmoEmotions() =D=> AnimationTriggerNode() =C=> wait
        #         wait: StateNode() =T(2)=> Say("") =Hear=>question
        #         do_it: TornToFace()
        #         do_it = F => do_it
        #         do_it = C => do_it
        
        # Code generated by genfsm on Mon Apr 24 17:48:10 2023:
        
        start = Start() .set_name("start") .set_parent(self)
        task1 = Say("How are you feeling today?") .set_name("task1") .set_parent(self)
        question = self.runGpt() .set_name("question") .set_parent(self)
        cozmoemotions1 = CozmoEmotions() .set_name("cozmoemotions1") .set_parent(self)
        animationtriggernode1 = AnimationTriggerNode() .set_name("animationtriggernode1") .set_parent(self)
        wait = StateNode() .set_name("wait") .set_parent(self)
        say1 = Say("") .set_name("say1") .set_parent(self)
        do_it = TornToFace() .set_name("do_it") .set_parent(self)
        
        nulltrans1 = NullTrans() .set_name("nulltrans1")
        nulltrans1 .add_sources(start) .add_destinations(task1,do_it)
        
        heartrans1 = HearTrans() .set_name("heartrans1")
        heartrans1 .add_sources(task1) .add_destinations(question)
        
        completiontrans1 = CompletionTrans() .set_name("completiontrans1")
        completiontrans1 .add_sources(question) .add_destinations(cozmoemotions1)
        
        datatrans1 = DataTrans() .set_name("datatrans1")
        datatrans1 .add_sources(cozmoemotions1) .add_destinations(animationtriggernode1)
        
        completiontrans2 = CompletionTrans() .set_name("completiontrans2")
        completiontrans2 .add_sources(animationtriggernode1) .add_destinations(wait)
        
        timertrans1 = TimerTrans(2) .set_name("timertrans1")
        timertrans1 .add_sources(wait) .add_destinations(say1)
        
        heartrans2 = HearTrans() .set_name("heartrans2")
        heartrans2 .add_sources(say1) .add_destinations(question)
        
        failuretrans1 = FailureTrans() .set_name("failuretrans1")
        failuretrans1 .add_sources(do_it) .add_destinations(do_it)
        
        completiontrans3 = CompletionTrans() .set_name("completiontrans3")
        completiontrans3 .add_sources(do_it) .add_destinations(do_it)
        
        return self

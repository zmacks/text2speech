# import pyttsx3
from openai import OpenAI
import openai
# import pyaudio
import wave
import logging
import os
from pathlib import Path
# import dotenv

# dotenv.load_dotenv()
# TODO: Look into the soundboard looking thing with buttons. (re: an interface)
# TODO: Map button press on the streamdeck to intent
# TODO: Draft prompt
# TODO: Generate bespoke text based on prompt
# TODO: Run on a server and invoke via LB'd REST API
# TODO: Transcribe the speaker's response into text
# TODO: Translate transcription into intent
# TODO: Craft prompt to respond to previous generated text (easy)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(filename='main.log', level=logging.DEBUG)

def list_engines():
    # list engines
    # TODO: The resource 'Engine' has been deprecated
    # engines = openai.Engine.list()

    for engine in engines.data:
        print(engine.id)

def complete(user_input,
             engine="text-davinci-003",
             model="gpt-3.5-turbo",
             temperature=0,
             max_tokens=16,
             top_p=1,
             logit_bias={},
             presence_penalty=0):
    logging.info("Completing prompt %s...", user_input)
    if type(user_input) == list:
        # create a _chat_ completion
        completion = complete_chat(
            messages=user_input,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            logit_bias=logit_bias)

    else:
        # create a completion
        completion = client.completions.create(engine=engine,
        prompt=user_input,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        logit_bias=logit_bias,
        presence_penalty=presence_penalty)

    logging.info("Created completion %s...",completion)
    return completion

def complete_chat(messages,model,logit_bias,temperature,max_tokens,top_p,presence_penalty):
    completion = client.chat.completions.create(model=model,
    messages=messages,
    logit_bias=logit_bias,
    temperature=temperature,
    max_tokens=max_tokens,
    top_p=top_p,
    presence_penalty=presence_penalty)

    return completion


def parse(data):
    logging.info("Parsing...")
    role = None
    finish_reason = None

    if data.get("object") == "chat.completion":
        finish_reason = data["choices"][0]["finish_reason"]
        content = data["choices"][0]["message"]["content"]
        role = data["choices"][0]["message"]["role"]

    elif data.get("object") == "text_completion":
        finish_reason = data["choices"][0]["finish_reason"]
        content = data["choices"][0].get("text")

    elif data.get("text"):
        content = data.get("text")

    return content, finish_reason, role

def get_voices(engine):
    voices = engine.getProperty('voices')
    return voices

# def text2speech(text,voice=None):
#     logging.info("Speaking...")
#     engine = pyttsx3.init()
#     voices = get_voices(engine)
#     voice = voices[7].id
#     engine.setProperty('voice', voice)
#     engine.say(text)
#     engine.runAndWait()

def text2speech(text):
    logging.info("Speaking...")
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    os.system(f"afplay {speech_file_path}")

def record(seconds=5,output_file = "output.wav"):
    logging.info("Recording...")
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = seconds
    WAVE_OUTPUT_FILENAME = output_file

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe(file_name):
    logging.info("Transcribing %s...",file_name)
    audio_file = open(file_name, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    logging.info("Transcribed: %s",transcript)
    return transcript

def mock_dialogue(system,content):
    # Crude simulation of dm<>player session 0
    dm1 = "What would you say about your life story?"
    response1 = "My life has been full of hardships, but they have only made me harder and tougher. I was born and raised in the Dwarven stronghold of Ardun, and ever since I can remember, I've been training myself in the highest martial arts, perfecting my skills with weapons, and learning the secrets of alchemy. My strong constitution and skill at arms have allowed me to survive many dangerous adventures and encounters. Now I fight for justice and defend the innocent, doing whatever it takes to ensure their safety.  So, if you need help, it looks like I'm your woman!"
    dm2 = "What's your home life like?"
    response2 = "Home life? Oh, that's an interesting topic! You see, as a dwarf, my home is not just a place, it's a community. My clan is my family, and I would do anything for them. We dwarves are known for being tough, stubborn, and loyal, and we take these traits to heart. We work together to make our settlement prosper and to protect it from danger. We have our own laws, our own customs, and our own way of life. At home, I'll be responsible for managing our clan's stores and finances, as well as directing our defense forces. But make no mistake: I will never hesitate to pick up my battleaxe and join the front lines!"
    dm3 = "Do you have any kids? Are you married?"
    response3 = "No, I'm not married and I don't have children. As a member of the Dwarven community, having a family is important to us, but it's not something to be taken lightly. I've been focused on my training and my duty to protect my clan, and I believe that I have a lot more to achieve before I can settle down and start a family. However, if the right person comes along, who knows? I might just change my mind! For the time being, though, I'm content with dedicating my life to fighting for my people and my home."

    dialogue = [
        {"role": "system", "content": f"{system}"},
        {"role": "user", "content": f"{dm1}"},
        {"role": "assistant", "content": f"{response1}"},
        {"role": "user", "content": f"{dm2}"},
        {"role": "assistant", "content": f"{response2}"},
        {"role": "user", "content": f"{dm3}"},
        {"role": "assistant", "content": f"{response3}"},
        {"role": "user", "content": f"{content}"}
    ]

    return dialogue

def main():
    """
    When run on a laptop, this script records your voice
    for n seconds, transcribes the user input, composes simulated
    chat dialogue with a DnD DM Assistant, then finally processes
    the chatbot's response through a text2speech generator.
    """
    # TODO: Allow the user to view the dialogue line by line interactively
    # TODO: Display a call-to-action in the CLI with instructions
    # file_name = "test.wav"
    file_name = "speech.mp3"
    # record(output_file=file_name,seconds=5)
    transcription = transcribe(file_name)
    content,_,_ = parse(transcription)

    # System prompt
    system = "You are a fictional character in my Dungeons and Dragons campaign. I want you to speak as a character who is hardy and tough and maybe a dwarf."

    # A crude dialogue between DM and PC
    dialogue = mock_dialogue(system, content, default="dnd")

    completion = complete(
        user_input=dialogue,
        max_tokens=250,
        temperature=1,
        top_p=1,
        presence_penalty=0
    )

    content,finish_reason,role = parse(completion)
    logging.info(f"[CONTENT] {content}")
    text2speech(content)

if __name__=="__main__":
    main()


import os
os.system("afplay file.mp3")     
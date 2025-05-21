import pyttsx3
import openai
import pyaudio
import wave
import logging
import os
import dotenv

dotenv.load_dotenv()
# TODO: Look into the soundboard looking thing with buttons. (re: an interface)
# TODO: Map button press on the streamdeck to intent
# TODO: Draft prompt
# TODO: Generate bespoke text based on prompt
# TODO: Run on a server and invoke via LB'd REST API
# TODO: Transcribe the speaker's response into text
# TODO: Translate transcription into intent
# TODO: Craft prompt to respond to previous generated text (easy)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def get_character_prompt(character_archetype, specific_traits=None):
    """
    Generates a system prompt for the AI based on character archetype and specific traits.
    """
    prompt = f"You are a character in a Dungeons and Dragons campaign. Your archetype is {character_archetype}."
    if specific_traits:
        traits_string = ", ".join(specific_traits)
        prompt += f" You are known for being {traits_string}."
    # Add more generic instructions or leave it open for further refinement.
    prompt += " Your speech should reflect these characteristics consistently."
    return prompt

logging.basicConfig(filename='main.log', level=logging.DEBUG)

def list_engines():
    # list engines
    engines = openai.Engine.list()

    for engine in engines.data:
        print(engine.id)

def complete(user_input,
             engine="text-davinci-003",
             model="gpt-3.5-turbo",
             temperature=0,
             max_tokens=16,
             top_p=1,
             logit_bias={},
             presence_penalty=0,
             frequency_penalty=0): # Added frequency_penalty
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
            frequency_penalty=frequency_penalty, # Added frequency_penalty
            logit_bias=logit_bias)

    else:
        # create a completion
        completion = openai.Completion.create(
            engine=engine,
            prompt=user_input,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            logit_bias=logit_bias,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty # Added frequency_penalty
        )

    logging.info("Created completion %s...",completion)
    return completion

def complete_chat(messages,model,logit_bias,temperature,max_tokens,top_p,presence_penalty,frequency_penalty): # Added frequency_penalty
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        logit_bias=logit_bias,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty # Added frequency_penalty
    )

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

def text2speech(text,voice=None):
    logging.info("Speaking...")
    engine = pyttsx3.init()
    voices = get_voices(engine)
    voice = voices[7].id
    engine.setProperty('voice', voice)
    engine.say(text)
    engine.runAndWait()

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
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    logging.info("Transcribed: %s",transcript)
    return transcript

def mock_dialogue(system, content):
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

    # CLI Instructions for the user
    print("Welcome to the AI Dialogue Companion!")
    record_seconds_val = 5 # This matches the default in record()
    print(f"I will start by recording your voice for {record_seconds_val} seconds to get your response.")
    print("Please speak clearly after you see the '* recording' message on the screen.")
    print("Let's begin!")
    print("-" * 30) # Separator line

    file_name = "test.wav"
    record(output_file=file_name,seconds=record_seconds_val) # Use the variable
    transcription = transcribe(file_name)
    content,_,_ = parse(transcription)
    print(f"You: {content}") # Print user's transcribed input

    # System prompt
    # system = "You are a fictional character in my Dungeons and Dragons campaign. I want you to speak as a character who is hardy and tough and maybe a dwarf."
    system_prompt = get_character_prompt("dwarf_warrior", ["hardy", "tough", "slightly greedy", "suspicious of elves"])
    
    # Initialize conversation history
    conversation_history = [{"role": "system", "content": system_prompt}]

    # Append user's transcribed input to history
    conversation_history.append({"role": "user", "content": content})
    
    # The line below is removed as per instructions, conversation_history is used instead
    # dialogue = mock_dialogue(system_prompt, content)

    # OpenAI API parameters for tuning text generation
    # temperature: Controls randomness. Lower values (e.g., 0.5-0.7) make the output more deterministic and persona-consistent.
    # Higher values (e.g., 0.7-0.9) can introduce more creativity but might deviate from the persona.
    # For a consistent character, start with a lower value.
    temperature = 0.7

    # max_tokens: The maximum number of tokens to generate. Ensure it's sufficient for the character to express themselves.
    # 250 is a reasonable starting point for a detailed response.
    max_tokens = 250

    # top_p: Nucleus sampling. An alternative to temperature. The model considers only tokens with top_p probability mass.
    # 1.0 means consider all tokens. Lower values (e.g., 0.9) can make output more focused.
    # Often, either temperature or top_p is used, not both tuned aggressively.
    top_p = 1.0

    # presence_penalty: Penalizes new tokens based on whether they appear in the text so far.
    # Positive values (e.g., 0.1-0.5, up to 2.0) discourage repetition of lines/topics.
    # Helps in maintaining a more natural and varied character voice.
    presence_penalty = 0.3

    # frequency_penalty: Penalizes new tokens based on their existing frequency in the text so far.
    # Positive values (e.g., 0.1-0.5, up to 2.0) discourage repetition of specific words/phrases.
    # Useful for preventing the AI from overusing certain terms, making the persona more nuanced.
    frequency_penalty = 0.2


    completion = complete(
        user_input=conversation_history, # Use conversation_history
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty
    )

    ai_content,finish_reason,ai_role = parse(completion) # Renamed content to ai_content for clarity
    
    # Append AI's response to history
    conversation_history.append({"role": ai_role if ai_role else "assistant", "content": ai_content})

    # Log the updated conversation history (optional, for verification)
    logging.info(f"Updated conversation history: {conversation_history}")

    print(f"AI: {ai_content}") # Print AI's textual response
    logging.info(f"[AI_CONTENT] {ai_content}") # Changed from [CONTENT]
    text2speech(ai_content) # Use ai_content

if __name__=="__main__":
    main()
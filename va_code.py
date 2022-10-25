import sys
import pyjokes
import speech_recognition as sr
import pyttsx3 as pytt
import pywhatkit as pwk
import datetime
import wikipedia
from weather_api import get_weather_info
from face_recog import run_facial_recognition, add_face_to_faces_folder, available_cameras

# installed SpeechRecognition
# installed PyAudio
# installed pyttsx3
# installed pywhatkit
# installed wikipedia
# installed pyjokes

# assistant's presentation
words = f'I am Jenny, your personal voice assistant. I can tell the time, play videos from youtube, ' \
        f'give information about current weather conditions in major' \
        f'cities around the world, perform searches in wikipedia and tell jokes.'

# create an instance of the Recognizer class from speech_recognition library
listener = sr.Recognizer()

# init function to get an engine instance for the speech synthesis
engine = pytt.init()

# female voice
voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
# another way to choose the voice
# voices = engine.getProperty('voices')
# voice_id = voices[1].id

# sets the female voice
engine.setProperty('voice', voice_id)

# sets the speed of speech
engine.setProperty('rate', 125)

wiki_signs = {'who', 'what', 'about'}


def wiki_command(text: str) -> str:
    """
    Processes the user's command so it can be used by wikipedia module.
    :param text:
    :return: command string
    """
    text_list = text.split()
    command = None
    if text.lower().startswith('who') or text.startswith('what'):
        command_list = text_list[2:]
        command = ' '.join(command_list)
    elif text.lower().startswith('tell me about'):
        command = text.replace('tell me about ', '')
    return command


def talk(text: str) -> None:
    """
    Speaks the text given as parameter.
    :param text: string
    :return: None
    """
    # say method on the engine that passing input text to be spoken
    engine.say(text)
    # run and wait method, it processes the voice commands.
    engine.runAndWait()


def get_user_name() -> str:
    """
    Listens to the user and gets their name.
    :return: str
    """
    with sr.Microphone() as source:
        # adjusting for ambient noise
        listener.adjust_for_ambient_noise(source)
        # listen to voice
        voice = listener.listen(source, 60)
        # recognize speech
        try:
            # get the user's name
            name = listener.recognize_google(voice)
            name = name.lower()
            return name
        except sr.UnknownValueError:
            talk('Could not understand name. Please repeat.')


def command_is_valid(text: str) -> bool:
    # list of valid commands
    valid_commands = ['play', 'time', 'joke', 'bye', 'goodbye', 'bye-bye', 'weather', 'who', 'what', 'about']
    for word in valid_commands:
        if word in text:
            return True


def accept_command() -> str or None:
    """
    Listens to the user and tries to get the command for the va. Tries maximum three times.
    :return: str or None
    """
    for i in range(3):
        with sr.Microphone() as source:
            talk('waiting for command')
            # adjusting for ambient noise
            listener.adjust_for_ambient_noise(source)
            # listen to voice
            voice = listener.listen(source, 60)
            try:
                # recognize speech
                command = listener.recognize_google(voice)
                command = command.lower()
                if 'jenny' in command:
                    command = command.replace('jenny', '')
                return command
            except sr.UnknownValueError:
                if i < 2:
                    talk('Could not understand command. Please repeat after message.')
                else:
                    talk('I am sorry. I am having a problem understanding command. Program terminated')
                    return


camera_check = False

current_user_name = None

program_active = True


def run_alexa():
    global camera_check, current_user_name
    # checking for available cameras
    if not camera_check:
        camera_check = True
        # function returns 0, 1 or None
        active_camera = available_cameras()
        if active_camera in (0, 1):
            talk('Initializing face recognition. Please look at your camera.')
            # get the username or result string if username is not obtained
            user_name = run_facial_recognition()
            # turn the username string into a list
            user_name_split = user_name.split(' ')
            # we have a user match
            if len(user_name_split) < 5:
                talk(f'Hello {user_name}. What can I do for you?')
                current_user_name = user_name
            # no face was discovered and the take_picture function returned None
            elif len(user_name_split) == 5:
                talk(user_name)
                talk(words)
            else:
                talk('User not recognized. As I can understand only native English names, please give an English name'
                     ' or alias as a closest English analogue to be used as identification.')
                # we have a picture with a face which doesn't match the known users' faces
                current_user_name = get_user_name()
                # saves the picture in the 'faces' folder naming the file with the username
                add_face_to_faces_folder(current_user_name)
                talk(f'{current_user_name} added to memory')
                talk(words)
        else:
            talk('Face recognition not possible. No cameras detected.')

    command = accept_command()
    global program_active
    if command is None:
        program_active = False
        return
    if not command_is_valid(command):
        talk('I am sorry, I could not find a valid command. Please try again.')
        return

    if 'play' in command:
        program_active = False
        # plays a song from youtube and terminates the program
        song = command.replace('play', '')
        talk('playing' + song)
        pwk.playonyt(song)
        if current_user_name is None:
            talk('I am glad to be of service. Have a nice day!')
            return
        talk(f'I am glad to be of service. Have a nice day{current_user_name}!')
        return
    elif 'time' in command:
        # tells the time
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f'Current time is {current_time}')
        return
    elif 'joke' in command:
        # tells a joke
        talk(pyjokes.get_joke())
        return
    elif 'bye' in command:
        # terminates the program
        program_active = False
        if current_user_name is None:
            talk('I am glad to be of service. Have a nice day!')
            return
        talk(f'I am glad to be of service. Have a nice day{current_user_name}!')
        return
    elif 'weather' in command:
        # gives current weather for chosen city
        city_name = command.split('in')[1]
        x = get_weather_info(city_name)
        for item in x:
            talk(item)
        return
    # checks if we have a wikipedia command.
    command_sentence = command.split()
    for word in command_sentence:
        if word in wiki_signs:
            try:
                item_of_interest = wiki_command(command)
                info = wikipedia.summary(item_of_interest, 1)
                talk(info)
            except:
                talk('I am sorry, item of interest not recognized.')
                break


while program_active:
    run_alexa()



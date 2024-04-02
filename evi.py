import os
import re
import time

import simpleaudio as sa

# Define the command to run your program
command = ["/Users/emedvedev/temp_projects/whisper.cpp/command",
           "-m", "/Users/emedvedev/temp_projects/whisper.cpp/models/ggml-medium.en.bin",
           "-t", "8",
           "--capture", "0",
           "--command-ms", "8000",
           "--prompt-ms", "2000"]

filename_tone = '/Users/emedvedev/temp_projects/evi/502716-RA-SFX-TESLA_Autopilot_Deactivate_-01.wav'
wave_obj = sa.WaveObject.from_wave_file(filename_tone)

from interpreter import interpreter

interpreter.llm.api_key = "<...>"
interpreter.auto_run = True
interpreter.llm.model = "gpt-3.5-turbo-0125"


# Hook function to be called when a command is detected
def on_command_detected(command_text):
    print(f"Command detected: {command_text}")


    interpreter.chat(command_text)  # Executes a single command

    if "bye" in command_text.lower():
        print("Exiting")
        os._exit(0)


def tail_file(filename, interval=0.5):
    """
    Continuously reads a file, yielding new lines as they are written.

    :param filename: Path to the file to be read.
    :param interval: Time (in seconds) to wait between each poll.
    """
    with open(filename, 'r') as file:
        # Move the pointer to the end of the file
        file.seek(0, 2)

        while True:
            print(".", end='')
            current_position = file.tell()
            line = file.readline()
            if not line:
                file.seek(current_position)
                time.sleep(interval)  # Wait a bit before checking for new content
            else:
                yield line.strip()


# Function to continuously read the command's output
def read_output():
    prompt_pattern = re.compile(r"process_general_transcription: The prompt has been recognized!")
    command_pattern = re.compile(r"process_general_transcription:   DEBUG: txt = '(.+?)', prob = (\d+\.\d+)%")
    general_pattern = re.compile(r"process_general_transcription: (Say the following phrase: .+)")

    for line in tail_file("/Users/emedvedev/temp_projects/whisper.cpp/output.log"):
        if not line:  # If no more output, the process might have terminated
            continue
        print("---------------" + line)  # For debugging, to see the stderr output
        if prompt_pattern.search(line):
            print("Hello!")  # If the prompt recognition log is detected

            play_obj = wave_obj.play()
            # play_obj.wait_done()  # Wait until sound has finished playing
        match = command_pattern.search(line)
        if match:
            # Extract the command text and probability, then call the hook function
            command_text = match.group(1)
            probability = match.group(2)  # You can use this probability if needed
            on_command_detected(command_text)
        else:
            # For any other log, print everything after "process_general_transcription:"
            general_match = general_pattern.search(line)
            if general_match:
                print(general_match.group(1))  # Print the captured group

read_output()



import psutil
import openai
import keyboard
import pyperclip

import configparser
import tkinter as tk
import sys
import os

latest = ""

def is_running() -> bool:
  current_pid = os.getpid()
  parent_pid = os.getppid()
  file_name = os.path.basename(sys.argv[0])

  process_list = []
  for proc in psutil.process_iter(['pid', 'name']):
    try:
      process_info = proc.info
      if process_info['name'] == file_name and not (process_info['pid'] == current_pid or process_info['pid'] == parent_pid) :
        process_list.append(process_info)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass

  if process_list:
    return True
  else:
    return False

def load_config(config_file: str) -> configparser.ConfigParser:
  # Load the configuration file.
  config = configparser.ConfigParser()
  config.read(config_file)
  return config

def display_window(answer: str) -> None:
  # Display a popup window with the given answer.
  root = tk.Tk()
  root.withdraw()

  popup = tk.Toplevel(root)
  popup.title("Update")
  popup.overrideredirect(True)
  popup.attributes("-alpha", float(config["Settings"]["PopOpacity"]))
  popup.geometry(config["Settings"]["PopPosition"])
  popup.attributes("-topmost", True)

  tk.Label(popup, text=answer, padx=10, pady=10).pack()

  popup.after(int(config["Settings"]["PopTimer"]), lambda: (popup.destroy(), root.quit()))

  root.mainloop()

def generate_response(message: str) -> str:
  # Generate a response for the given message using the OpenAI API.
  try:
    response = openai.ChatCompletion.create(
      model=config["Settings"]["Model"], 
      messages=[
        { "role": "system", "content": config["Settings"]["PromptSystem"] },
        { "role": "user", "content": f'{config["Settings"]["PromptUser"]} {message}' }
      ]
    )

    return response['choices'][0]['message']['content']
  except Exception as e:
    return f"Error generating response: {e}"

def on_key_event(e: keyboard.KeyboardEvent) -> None:
  # Handle the key event.
  global config, latest

  key_values = [value for value in config['Keys'].values()]
  if e.event_type == keyboard.KEY_DOWN and e.name in key_values:
    config = load_config('config.cfg')
    copied_text = pyperclip.paste()
    response = generate_response(copied_text)
    if e.name == config["Keys"]["KeyPop"]:
      latest = response
      display_window(response)
    elif e.name == config["Keys"]["KeyRepop"]:
      display_window(latest)

if __name__ == "__main__":
  if is_running():
    sys.exit(0)
  
  config = load_config('config.cfg')
  openai.api_key = config["Api"]["OpenAiKey"]

  keyboard.hook(on_key_event)
  keyboard.wait()
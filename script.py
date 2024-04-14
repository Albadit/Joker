import psutil
import openai
import pyperclip
from pynput import mouse, keyboard

import configparser
import tkinter as tk
import sys
import os

latest = ''
pause = True
config_name = 'config.ini'

def is_running() -> bool:
  current_pid = os.getpid()
  parent_pid = os.getppid()
  file_name = os.path.basename(sys.argv[0])

  process_list = []
  for proc in psutil.process_iter(['pid', 'name']):
    try:
      process_info = proc.info
      if process_info['name'] == file_name and not (process_info['pid'] == current_pid or process_info['pid'] == parent_pid):
        process_list.append(process_info)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass

  if process_list: return True
  else: return False

def load_config(config_file: str) -> configparser.ConfigParser:
  config = configparser.ConfigParser()
  config.read(config_file)
  return config

def display_window(answer: str) -> None:
  root = tk.Tk()
  root.withdraw()

  popup = tk.Toplevel(root)
  popup.title("Update")
  popup.overrideredirect(True)
  popup.attributes("-alpha", float(config["window"]["alpha"]))
  popup.geometry(config["window"]["position"])
  popup.attributes("-topmost", True)

  tk.Label(popup, text=answer, padx=10, pady=10).pack()

  popup.after(int(config["window"]["display_time"]), lambda: (popup.destroy(), root.quit()))

  root.mainloop()

def generate_response(message: str) -> str:
  try:
    response = openai.ChatCompletion.create(
      model=config["openai"]["model"], 
      messages=[
        { "role": "system", "content": config["openai"]["prompt_system"] },
        { "role": "user", "content": f'{config["openai"]["prompt_user"]} {message}' }
      ]
    )

    return response['choices'][0]['message']['content']
  except Exception as e:
    return f"Error generating response: {e}"

def on_key_press(key):
  global pause, latest

  try:
    key_name = key.char or key.name
  except AttributeError:
    key_name = str(key)
  
  key_values = [value for value in config['key'].values()]
  if key_name in key_values:
    if key_name == config["key"]["key_exit"]:
      pause = not pause
    elif key_name == config["key"]["key_pop"] and pause:
      copied_text = pyperclip.paste()
      response = generate_response(copied_text)
      latest = response
      display_window(response)
    elif key_name == config["key"]["key_repop"] and pause:
      display_window(latest)

def on_key_release(key):
  pass

def on_mouse_click(x, y, button, pressed):
  if button == mouse.Button.right and pressed:
    keyboard_controller = keyboard.Controller()
    with keyboard_controller.pressed(keyboard.Key.ctrl):
      keyboard_controller.press('c')
      keyboard_controller.release('c')

if __name__ == "__main__":
  if is_running():
    sys.exit(0)
  
  config = load_config(config_name)
  openai.api_key = config["openai"]["api_key"]

  keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
  mouse_listener = mouse.Listener(on_click=on_mouse_click)

  keyboard_listener.start()
  mouse_listener.start()

  keyboard_listener.join()
  mouse_listener.join()
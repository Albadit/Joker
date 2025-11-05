import psutil
from openai import OpenAI
import pyperclip
from pynput import mouse, keyboard
import configparser
import tkinter as tk
import sys
import os
from typing import Optional

# Global state
latest = ''
disable = False
config_name = 'config.ini'
config: Optional[configparser.ConfigParser] = None
client: Optional[OpenAI] = None

def is_running() -> bool:
  """Check if another instance of this script is already running."""
  current_pid = os.getpid()
  parent_pid = os.getppid()
  file_name = os.path.basename(sys.argv[0])

  for proc in psutil.process_iter(['pid', 'name']):
    try:
      process_info = proc.info
      if (process_info['name'] == file_name and 
          process_info['pid'] not in (current_pid, parent_pid)):
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      pass

  return False

def load_config(config_file: str) -> configparser.ConfigParser:
  """Load and validate configuration from INI file."""
  if not os.path.exists(config_file):
    raise FileNotFoundError(f"Configuration file '{config_file}' not found")
  
  config = configparser.ConfigParser()
  config.read(config_file)
  
  # Define required sections and their keys
  required_config = {
    'key': ['key_exit', 'key_pop', 'key_repop'],
    'openai': ['api_key', 'model', 'prompt_system', 'prompt_user'],
    'window': ['alpha', 'display_time', 'position']
  }
  
  # Keys that can be empty
  optional_keys = {'prompt_system', 'prompt_user'}
  
  # Validate required sections and keys
  for section, keys in required_config.items():
    if not config.has_section(section):
      raise ValueError(f"Missing required section '[{section}]' in config file")
    
    for key in keys:
      if not config.has_option(section, key):
        raise ValueError(f"Missing required key '{key}' in section '[{section}]'")
      
      # Only validate non-empty for keys that aren't optional
      if key not in optional_keys:
        value = config.get(section, key).strip()
        if not value:
          raise ValueError(f"Empty value for '{key}' in section '[{section}]'. Please configure it in {config_file}")
  
  return config

def calculate_window_dimensions(answer: str, screen_width: int, screen_height: int, position: str) -> tuple[int, int]:
  """Calculate optimal window dimensions based on content and screen size.
  
  Args:
    answer: The text content to display
    screen_width: Screen width in pixels
    screen_height: Screen height in pixels
    position: Window position string (e.g., "+300+200")
  
  Returns:
    Tuple of (width_in_chars, height_in_lines)
  """
  # Parse position from config (e.g., "+300+200")
  x_offset = int(position.split('+')[1]) if '+' in position else 300
  y_offset = int(position.split('+')[2]) if position.count('+') >= 2 else 200
  
  # Calculate maximum available dimensions
  max_width_pixels = screen_width - x_offset - 20  # 20px margin
  max_height_pixels = screen_height - y_offset - 40  # 40px margin for taskbar
  
  # Convert pixels to approximate character/line dimensions
  # Roughly 8 pixels per character, 20 pixels per line
  max_width_chars = max_width_pixels // 8
  max_height_lines = max_height_pixels // 20
  
  # Calculate dynamic dimensions based on text
  lines = answer.split('\n')
  max_line_length = max(len(line) for line in lines) if lines else 0
  num_lines = len(lines)
  
  # Calculate width (characters) - Min 30, max based on screen size
  width = min(max(30, max_line_length + 5), max_width_chars)
  
  # Calculate height (lines) - Min 3, max based on screen size
  height = min(max(3, num_lines + 2), max_height_lines)
  
  return width, height


def display_window(answer: str) -> None:
  """Display a temporary popup window with the response."""
  if not answer:
    return
  
  root = tk.Tk()
  root.withdraw()

  popup = tk.Toplevel(root)
  popup.title("Response")
  popup.overrideredirect(True)
  popup.attributes("-alpha", float(config["window"]["alpha"]))
  popup.attributes("-topmost", True)

  # Get screen dimensions
  screen_width = root.winfo_screenwidth()
  screen_height = root.winfo_screenheight()
  position = config["window"]["position"]
  
  # Calculate optimal dimensions
  width, height = calculate_window_dimensions(answer, screen_width, screen_height, position)
  
  # Add text widget with wrapping for long responses
  text_widget = tk.Text(popup, wrap=tk.WORD, padx=10, pady=10, width=width, height=height)
  text_widget.insert("1.0", answer)
  text_widget.config(state=tk.DISABLED)
  text_widget.pack()
  
  # Update window to get actual size, then position it
  popup.update_idletasks()
  popup.geometry(position)

  display_time = int(config["window"]["display_time"])

  popup.after(display_time, lambda: (popup.destroy(), root.quit()))
  root.mainloop()

def generate_response(message: str) -> str:
  """Generate AI response using OpenAI API."""
  if not message or not message.strip():
    return "No text provided"
  
  if client is None:
    return "Error: OpenAI client not initialized"
  
  try:
    response = client.chat.completions.create(
      model=config["openai"]["model"], 
      messages=[
        {"role": "system", "content": config["openai"]["prompt_system"]},
        {"role": "user", "content": f'{config["openai"]["prompt_user"]} {message}'}
      ]
    )

    return response.choices[0].message.content
  except Exception as e:
    return f"Error generating response: {e}"

def on_key_press(key) -> None:
  """Handle keyboard press events."""
  global disable, latest

  # Get the key name in a format that matches config
  try:
    if hasattr(key, 'char') and key.char:
      key_name = key.char
    else:
      # For special keys, format as "Key.name"
      key_name = f"Key.{key.name}" if hasattr(key, 'name') else str(key)
  except AttributeError:
    key_name = str(key)
  
  # Cache config keys to avoid repeated dictionary access
  key_exit = config["key"]["key_exit"]
  key_pop = config["key"]["key_pop"]
  key_repop = config["key"]["key_repop"]
  
  if key_name == key_exit:
    disable = not disable
    print(f"{'Disabled' if disable else 'Active'}")
  elif key_name == key_pop and not disable:
    copied_text = pyperclip.paste()
    if copied_text:
      print(f"Processing: {copied_text[:50]}...")
      response = generate_response(copied_text)
      latest = response
      display_window(response)
    else:
      print("No text in clipboard")
  elif key_name == key_repop and not disable:
    if latest:
      display_window(latest)
    else:
      print("No previous response to display")

def on_key_release(key) -> None:
  """Handle keyboard release events."""
  pass

def on_mouse_click(x: int, y: int, button, pressed: bool) -> None:
  """Handle mouse click events - auto-copy on right-click."""
  if not disable and button == mouse.Button.right and pressed:
    keyboard_controller = keyboard.Controller()
    with keyboard_controller.pressed(keyboard.Key.ctrl):
      keyboard_controller.press('c')
      keyboard_controller.release('c')

if __name__ == "__main__":
  # Prevent multiple instances
  if is_running():
    print("Another instance is already running. Exiting.")
    sys.exit(0)
  
  try:
    # Load configuration
    config = load_config(config_name)
    
    # Validate API key
    api_key = config["openai"]["api_key"]
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    print("Joker Assistant started successfully")
    print(f"Press {config['key']['key_exit']} to toggle disable")
    print(f"Press {config['key']['key_pop']} to generate response")
    print(f"Press {config['key']['key_repop']} to show last response")
    
    # Start listeners
    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_click=on_mouse_click)

    keyboard_listener.start()
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()
    
  except Exception as e:
    print(f"Fatal error: {e}")
    sys.exit(1)
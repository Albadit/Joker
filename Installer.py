import winreg
from pathlib import Path
import win32com.client
import ctypes
import os
import sys
import subprocess
import shutil

script_content = '''
import psutil
import openai
import keyboard
import pyperclip

import configparser
import tkinter as tk
import sys
import os

latest = ''

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
  popup.title('Update')
  popup.overrideredirect(True)
  popup.attributes('-alpha', float(config['Settings']['PopOpacity']))
  popup.geometry(config['Settings']['PopPosition'])
  popup.attributes('-topmost', True)

  tk.Label(popup, text=answer, padx=10, pady=10).pack()

  popup.after(int(config['Settings']['PopTimer']), lambda: (popup.destroy(), root.quit()))

  root.mainloop()

def generate_response(message: str) -> str:
  # Generate a response for the given message using the OpenAI API.
  try:
    response = openai.ChatCompletion.create(
      model=config['Settings']['Model'], 
      messages=[
        { 'role': 'system', 'content': config['Settings']['PromptSystem'] },
        { 'role': 'user', 'content': f'{config['Settings']['PromptUser']} {message}' }
      ]
    )

    return response['choices'][0]['message']['content']
  except Exception as e:
    return f'Error generating response: {e}'

def on_key_event(e: keyboard.KeyboardEvent) -> None:
  # Handle the key event.
  global config, latest

  key_values = [value for value in config['Keys'].values()]
  if e.event_type == keyboard.KEY_DOWN and e.name in key_values:
    config = load_config('config.cfg')
    copied_text = pyperclip.paste()
    response = generate_response(copied_text)
    if e.name == config['Keys']['KeyPop']:
      latest = response
      display_window(response)
    elif e.name == config['Keys']['KeyRepop']:
      display_window(latest)

if __name__ == '__main__':
  if is_running():
    sys.exit(0)
  
  config = load_config('config.cfg')
  openai.api_key = config['Api']['OpenAiKey']

  keyboard.hook(on_key_event)
  keyboard.wait()
'''

def is_admin():
  '''Check if the script is running with administrative privileges.'''
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False

def create_config(config_path: Path, file_name: str) -> None:
  settings = {
    'Api': {
      'OpenAiKey': '',
    },
    'Settings': {
      'PopTimer': '3000',
      'PopPosition': '+300+200',
      'PopOpacity': '0.5',
      'Model': 'gpt-4',
      'PromptSystem': 'You are a helpful assistant specialized in answering multiple-choice questions.',
      'PromptUser': 'Give me only the correct answer and nothing else:',
    },
    'Keys': {
      'KeyPop': '~',
      'KeyRepop': '`',
    }
  }

  contents = '\n'.join(f'[{section}]\n' + '\n'.join(f'{k} = {v}' for k, v in options.items()) + '\n' for section, options in settings.items())
  Path(config_path / file_name).write_text(contents)
  print(f'{file_name} has been Generate successful.')

def task_scheduler(setup_path: Path, script_name: str) -> None:
  # Connect to the Task Scheduler
  scheduler = win32com.client.Dispatch('Schedule.Service')
  scheduler.Connect()
  root_folder = scheduler.GetFolder('\\')

  # Create a new task definition
  task_def = scheduler.NewTask(0)

  # Set registration info
  task_def.RegistrationInfo.Description = f'{script_name} Task'
  task_def.RegistrationInfo.Author = f'{script_name}'

  # Create Triggers
  # Boot Trigger
  task_def.Triggers.Create(8)  # 8 = Boot Trigger

  # Logon Trigger
  task_def.Triggers.Create(9)  # 9 = Logon Trigger

  # Session State Change Trigger for Session Unlock
  session_unlock_trigger = task_def.Triggers.Create(11)  # 11 = Session State Change Trigger
  session_unlock_trigger.StateChange = 8  # 8 = Session unlock

  # Idle Trigger
  task_def.Triggers.Create(6)  # 6 = Idle Trigger

  # Session State Change Trigger for Console Connect
  console_connect_trigger = task_def.Triggers.Create(11)  # Reusing 11 for a different session state change
  console_connect_trigger.StateChange = 4  # 4 = Console connect

  # Set the principal for the task
  task_def.Principal.LogonType = 3  # 3 = Interactive Token
  task_def.Principal.RunLevel = 1   # 1 = Highest Available

  # Set task settings
  settings = task_def.Settings
  settings.MultipleInstances = 2  # 2 = Ignore New
  settings.DisallowStartIfOnBatteries = False
  settings.StopIfGoingOnBatteries = False
  settings.AllowHardTerminate = False
  settings.StartWhenAvailable = True
  settings.RunOnlyIfNetworkAvailable = False
  settings.Enabled = True
  settings.Hidden = False
  settings.RunOnlyIfIdle = False
  settings.WakeToRun = True
  settings.ExecutionTimeLimit = 'P1D'  # Period of one day
  settings.Priority = 7

  # Idle settings
  settings.IdleSettings.StopOnIdleEnd = True
  settings.IdleSettings.RestartOnIdle = False

  # Set an action
  action = task_def.Actions.Create(0)  # 0 = Execute
  action.Path = f'{setup_path}\\{script_name}.exe'
  action.Arguments = f'{setup_path}\\config.cfg'
  action.WorkingDirectory = f'{setup_path}' 

  # Register the task
  task_name = f'\\{script_name}'
  root_folder.RegisterTaskDefinition(task_name, task_def, 6, '', '', 3)  # 6 = CreateOrUpdate, 3 = TaskLogonType.InteractiveToken
  print('Task Scheduler has been created successful.')

def install_libraries():
  libs = ['pyinstaller', 'configparser', 'pyperclip', 'keyboard', 'openai==0.28', 'psutil']

  for lib in libs:
    command = f'pip install {lib}'
    subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  
  print('All libraries has been installed successful.')

def install_script(setup_path: Path, script_code: str, script_name: str) -> None:
  install_libraries()
  create_config(setup_path, 'config.cfg')
  filepath = str(Path(setup_path / script_name)).replace("\\", "\\\\")
  with open(filepath + '.py', 'w') as script_file:
    script_file.write(script_code)

  icon = input('Please paste the url path of the icon: ')
  while '.ico' not in icon:
    icon = input('The icon format need to be (.ico): ')

  command = f'pyinstaller --noconfirm --onefile --noconsole --add-data "config.cfg;." --icon={icon.replace('\\', '\\\\')} --hidden-import psutil --hidden-import openai --hidden-import keyboard --hidden-import pyperclip {filepath + '.py'}'
  try:
    # Note: Using subprocess.Popen instead of subprocess.run
    with subprocess.Popen(command, cwd=setup_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
      # Read output and error streams
      stdout, stderr = process.communicate()  # Waits for process to complete
      print("STDOUT:")
      print(stdout)
      print("STDERR:")
      print(stderr)
  except Exception as err:
    print('Error encountered:')
    print(err)

  os.system(f'move "{setup_path}\\dist\\{script_name + '.exe'}" "{setup_path}"')
  os.remove(filepath + '.spec')
  os.remove(filepath + '.py')
  os.removedirs(Path(setup_path / 'dist'))
  shutil.rmtree(Path(setup_path / 'build'))

  print(f'{script_name + '.exe'}.exe has been installed successful.')

def create_shortcut(setup_path: Path, cfg_path: Path, shortcut_link: Path) -> None:
  shortcut = win32com.client.Dispatch('WScript.Shell').CreateShortcut(str(shortcut_link))
  shortcut.Targetpath = str(cfg_path)
  shortcut.WorkingDirectory = str(setup_path)
  shortcut.IconLocation = str(cfg_path)
  shortcut.save()
  print('Shorcut has been created successful.')

def unistall(setup_path: Path, script_name: str) -> None:
  try:
    shutil.rmtree(Path(setup_path))
  except Exception as er:
    print(er)

  try:
    subprocess.run(f'schtasks /Delete /TN "{script_name}" /F', check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  except Exception as er:
    print(er)

  print(f'The script {script_name} has been remove successful.')

def parse_selection(install_list: list) -> list:
  selected_indices = []

  while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Select the components to install/reinstall:')
    for i, item in enumerate(install_list):
      print(f'{i + 1}. {item}')
    print(f'{len(install_list) + 1}. All')
    print('Selected:', ', '.join(selected_indices))

    selection = input('Enter your choice (e.g., 1, 3-4, 5 for all, Press enter if you\'re done): ')

    # Check for 'Enter' to finish selection
    if selection == '':
      break
    elif selection == f'{len(install_list) + 1}':
      return [int(i + 1) for i in range(len(install_list))]

    # Convert selection to integer and validate
    try:
      selection_int = int(selection)
      if selection_int < 1 or selection_int > len(install_list) + 2:
        print('Invalid selection. Please enter a valid number.')
        input(exit_text)
        continue
    except ValueError:
      print('Invalid input. Please enter a number.')
      input(exit_text)
      continue

    # Handle addition or removal of selection
    if selection in selected_indices:
      selected_indices.remove(selection)
    else:
      selected_indices.append(selection)

  # Converting selected_indices to integers and sorting
  return sorted([int(idx) for idx in selected_indices])

def setup() -> None:
  key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
  try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
      paths = {name: winreg.QueryValueEx(key, name)[0] for name in ('Personal', 'Desktop')}
  except (FileNotFoundError, OSError) as e:
    print(f'Error accessing registry: {e}')
    return
  
  script_name = input('Script name (you can name the script how you like it): ').replace(' ', '_')

  setup_path = Path(paths['Personal'], script_name)

  install_list = ['Install exe', 'Scheduler Tasks', 'Unistall']

  if setup_path.exists():
    context = 'The setup path already exists. Do you want to install/reinstall/unistall components (y/n): '
    user_input = input(context).strip().lower()
    while user_input not in ['no', 'n' , 'yes', 'y']:
      os.system('cls')
      user_input = input(context).strip().lower()
      if user_input == ['no', 'n']:
        return
    selected_index = parse_selection(install_list)
  else:
    selected_index = [int(i + 1) for i in range(len(install_list))]
    selected_index.pop()
    setup_path.mkdir(parents=True, exist_ok=True)

  if 1 in selected_index:
    install_script(setup_path, script_content, script_name)
  if 2 in selected_index:
    task_scheduler(setup_path, script_name)
  if 3 in selected_index:
    unistall(setup_path, script_name)

  # generate_config(setup_path / 'config.cfg')
  # task_scheduler(setup_path)
  # cfg_path = download_exe(setup_path)
  # create_shortcut(setup_path, cfg_path, Path(paths['Desktop'], 'School Easy.lnk'))

if __name__ == '__main__':
  if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
    sys.exit(0)

  exit_text = 'Press Enter to continue...'
  setup()
  print('Your done. You\'re ready to go.')
  input(exit_text)

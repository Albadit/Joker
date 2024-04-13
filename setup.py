import os
import sys
import ctypes
import urllib.request
from configparser import ConfigParser
from win32com.client import Dispatch
import shutil

def exit_sys():
  input("Press Enter to close...")
  sys.exit(-1)

def permission(question):
  response = input(f"{question} (y/n): ")
  return response.lower() == 'y'

def is_admin():
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False

def relaunch_as_admin():
  try:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
  except Exception as e:
    print("Operation cancelled by user or failed.")
    print(str(e))

def delete_task_scheduler(script_name):
  scheduler = Dispatch("Schedule.Service")
  scheduler.Connect()
  root_folder = scheduler.GetFolder("\\")
  try:
    root_folder.DeleteTask(script_name, 0)
    print(f"Task '{script_name}' successfully deleted.")
  except Exception as e:
    print(f"Failed to delete task. Error: {str(e)}")

def create_task_scheduler(script_path, script_name, config_name):
  scheduler = Dispatch("Schedule.Service")
  scheduler.Connect()
  root_folder = scheduler.GetFolder("\\")
  
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
  settings.Enabled = True
  settings.ExecutionTimeLimit = "P1D"  # Period of one day
  settings.Priority = 7

  # Idle settings
  settings.IdleSettings.StopOnIdleEnd = True
  settings.IdleSettings.RestartOnIdle = False

  # Set an action
  action = task_def.Actions.Create(0)  # 0 = Execute
  action.Path = f'{script_path}\\{script_name}.exe'
  action.Arguments = f'{script_path}\\{config_name}'
  action.WorkingDirectory = f'{script_path}' 
  
  try:
    root_folder.RegisterTaskDefinition(script_name, task_def, 6, None, None, 3)
    print(f"Task '{script_name}' successfully registered.")
  except Exception as e:
    print(f"Failed to register task. Error: {str(e)}")

def config(script_path, config_name):
  settings = {
    'openai': {
      'api_key': '',
      'model': 'gpt-4',
      'prompt_system': 'You are a helpful assistant specialized in answering multiple-choice questions.',
      'prompt_user': 'Give me only the correct answer and nothing else:'
    },
    'window': {
      'alpha': '0.5',
      'position': '+300+200',
      'display_time': '3000'
    },
    'key': {
      'key_pop': '~',
      'key_repop': '`',
      'key_exit': 'esc'
    }
  }
  
  config_path = os.path.join(script_path, config_name)
  config = ConfigParser()
  config.read_dict(settings)
  with open(config_path, 'w') as configfile:
    config.write(configfile)
  print(f"{config_name} has been generated successfully.")

def delete_setup(script_path, script_name):
  if permission("Do you want to uninstall it?"):
    delete_task_scheduler(script_name)
    try:
      shutil.rmtree(script_path)
      print("Folder and its contents have been deleted.")
    except Exception as e:
      print(f"Error: {str(e)}")

def download_exe(setup_path, script_name):
  try:
    url = 'https://raw.githubusercontent.com/Albadit/Joker/main/app/joker.exe'
    cfg_path = f'{setup_path}\\{script_name}.exe'
    urllib.request.urlretrieve(url, cfg_path)
    print(f'The {script_name}.exe has been downloaded.')
  except Exception as e: 
    print(e)

def setup(script_path, script_name):
  config_name = "config.ini"
  create_task_scheduler(script_path, script_name, config_name)
  config(script_path, config_name)
  download_exe(script_path, script_name)

def menu():
  # folder_path = "C:\\Users\\ardit\\Documents"
  # script_name = "zzz"

  folder_path = input("Folder path of your script: ")
  script_name = input("Script name: ")
  script_path = os.path.join(folder_path, script_name)

  if not os.path.exists(script_path):
    os.makedirs(script_path, exist_ok=True)
    print("The folder was created successfully.\n")
    setup(script_path, script_name)
  else:
    print("The folder already exists.\n")
    delete_setup(script_path, script_name)

  exit_sys()

def main():
  if not is_admin():
    relaunch_as_admin()
    return
  print("Hello, from jokers!\n")
  menu()

if __name__ == "__main__":
  main()

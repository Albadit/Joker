import os
import sys
import ctypes
import urllib.request
from configparser import ConfigParser
from win32com.client import Dispatch
import shutil

def exit_sys(code: int = 0) -> None:
  """Exit the program after user confirmation."""
  input("\nPress Enter to close...")
  sys.exit(code)

def permission(question: str) -> bool:
  """Ask user for yes/no confirmation."""
  while True:
    response = input(f"{question} (y/n): ").lower().strip()
    if response in ('y', 'yes'):
      return True
    elif response in ('n', 'no'):
      return False
    else:
      print("Invalid input. Please enter 'y' or 'n'.")

def is_admin() -> bool:
  """Check if the script is running with administrator privileges."""
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except Exception as e:
    print(f"Warning: Failed to check admin status - {e}")
    return False

def relaunch_as_admin() -> None:
  """Relaunch the script with administrator privileges."""
  try:
    print("This script requires administrator privileges.")
    print("Requesting elevation...")
    ctypes.windll.shell32.ShellExecuteW(
      None, "runas", sys.executable, 
      " ".join([f'"{arg}"' for arg in sys.argv]), 
      None, 1
    )
  except Exception as e:
    print(f"Failed to elevate privileges: {e}")
    print("Please run this script as administrator.")

def delete_task_scheduler(script_name: str) -> bool:
  """Delete a task from Windows Task Scheduler."""
  try:
    scheduler = Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")
    root_folder.DeleteTask(script_name, 0)
    print(f"✓ Task '{script_name}' successfully deleted.")
    return True
  except Exception as e:
    print(f"✗ Failed to delete task '{script_name}': {e}")
    return False

def create_task_scheduler(script_path: str, script_name: str, config_name: str) -> bool:
  """Create a Windows Task Scheduler task to run the script automatically."""
  try:
    scheduler = Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")
    
    # Create a new task definition
    task_def = scheduler.NewTask(0)

    # Set registration info
    task_def.RegistrationInfo.Description = f'{script_name} - AI Assistant Task'
    task_def.RegistrationInfo.Author = 'Joker Setup'

    # Create essential triggers
    # Logon Trigger - Run at user login (most important)
    task_def.Triggers.Create(9)

    # Session Unlock Trigger - Run when user unlocks PC
    session_unlock_trigger = task_def.Triggers.Create(11)
    session_unlock_trigger.StateChange = 8  # Session unlock

    # Set the principal for the task
    task_def.Principal.LogonType = 3  # Interactive Token
    task_def.Principal.RunLevel = 1   # Highest Available

    # Set task settings
    settings = task_def.Settings
    settings.MultipleInstances = 2  # Ignore New (don't start if already running)
    settings.DisallowStartIfOnBatteries = False
    settings.StopIfGoingOnBatteries = False
    settings.Enabled = True
    settings.ExecutionTimeLimit = "PT0S"  # No time limit
    settings.Priority = 7
    settings.Hidden = False

    # Set an action
    action = task_def.Actions.Create(0)  # Execute
    action.Path = os.path.join(script_path, f'{script_name}.exe')
    action.WorkingDirectory = script_path
    
    # Register the task
    root_folder.RegisterTaskDefinition(
      script_name, 
      task_def, 
      6,    # Create or Update
      None, # No user
      None, # No password
      3     # Interactive Token
    )
    print(f"✓ Task '{script_name}' successfully registered.")
    print(f"  - Triggers: Logon, Session Unlock")
    return True
    
  except Exception as e:
    print(f"✗ Failed to register task: {e}")
    return False

def config(script_path: str, config_name: str) -> bool:
  """Generate default configuration file."""
  settings = {
    'key': {
      'key_exit': 'Key.esc',
      'key_pop': '1',
      'key_repop': '2'
    },
    'openai': {
      'api_key': '',
      'model': 'gpt-4',
      'prompt_system': 'You are a helpful assistant specialized in answering multiple-choice questions.',
      'prompt_user': 'Give me only the correct answer and nothing else:'
    },
    'window': {
      'alpha': '0.5',
      'display_time': '3000',
      'position': '+300+200'
    }
  }
  
  try:
    config_path = os.path.join(script_path, config_name)
    config_parser = ConfigParser()
    config_parser.read_dict(settings)
    
    with open(config_path, 'w') as configfile:
      config_parser.write(configfile)
    
    print(f"✓ {config_name} generated successfully.")
    print(f"  Location: {config_path}")
    print(f"  ⚠ Remember to add your OpenAI API key!")
    return True
    
  except Exception as e:
    print(f"✗ Failed to create config file: {e}")
    return False

def delete_setup(script_path: str, script_name: str) -> None:
  """Uninstall the application by removing task scheduler entry and files."""
  print("\n=== UNINSTALL MODE ===")
  print(f"Target: {script_path}")
  
  if not permission("Do you want to uninstall Joker?"):
    print("Uninstall cancelled.")
    return
  
  print("\nUninstalling...")
  
  # Delete task scheduler entry
  task_deleted = delete_task_scheduler(script_name)
  
  # Delete folder and contents
  try:
    if os.path.exists(script_path):
      shutil.rmtree(script_path)
      print(f"✓ Folder '{script_path}' and its contents have been deleted.")
    else:
      print(f"ℹ Folder '{script_path}' does not exist.")
  except PermissionError:
    print(f"✗ Permission denied. Cannot delete '{script_path}'.")
    print("  Please close any running instances and try again.")
  except Exception as e:
    print(f"✗ Failed to delete folder: {e}")
  
  if task_deleted:
    print("\n✓ Uninstall completed successfully!")
  else:
    print("\n⚠ Uninstall completed with warnings.")

def download_exe(setup_path: str, script_name: str) -> bool:
  """Download the executable from GitHub repository latest release."""
  api_url = 'https://api.github.com/repos/Albadit/Joker/releases/latest'
  exe_path = os.path.join(setup_path, f'{script_name}.exe')
  
  try:
    print(f"\nFetching latest release information...")
    print(f"  API: {api_url}")
    
    # Get release information from GitHub API
    with urllib.request.urlopen(api_url) as response:
      import json
      release_data = json.loads(response.read().decode())
    
    # Find joker.exe in assets
    download_url = None
    for asset in release_data.get('assets', []):
      if asset.get('name') == 'joker.exe':
        download_url = asset.get('browser_download_url')
        file_size = asset.get('size', 0)
        break
    
    if not download_url:
      print(f"✗ joker.exe not found in latest release")
      print(f"  Release: {release_data.get('tag_name', 'unknown')}")
      return False
    
    print(f"✓ Found joker.exe in release {release_data.get('tag_name', 'unknown')}")
    print(f"  Size: {file_size:,} bytes")
    print(f"\nDownloading {script_name}.exe...")
    print(f"  Source: {download_url}")
    
    urllib.request.urlretrieve(download_url, exe_path)
    
    if os.path.exists(exe_path):
      actual_size = os.path.getsize(exe_path)
      print(f"✓ Downloaded successfully ({actual_size:,} bytes)")
      print(f"  Location: {exe_path}")
      return True
    else:
      print(f"✗ File not found after download")
      return False
      
  except urllib.error.URLError as e:
    print(f"✗ Network error: {e}")
    print("  Please check your internet connection.")
    return False
  except Exception as e:
    print(f"✗ Download failed: {e}")
    return False

def setup(script_path: str, script_name: str) -> bool:
  """Perform complete setup: create config, download exe, and setup task scheduler."""
  config_name = "config.ini"
  
  print("\n=== INSTALLATION MODE ===")
  print(f"Installing to: {script_path}\n")
  
  success = True
  
  # Step 1: Generate config
  print("[1/3] Generating configuration file...")
  if not config(script_path, config_name):
    success = False
  
  # Step 2: Download executable
  print("\n[2/3] Downloading executable...")
  if not download_exe(script_path, script_name):
    success = False
    print("  ⚠ You may need to manually copy the .exe file")
  
  # Step 3: Create task scheduler
  print("\n[3/3] Setting up Task Scheduler...")
  if not create_task_scheduler(script_path, script_name, config_name):
    success = False
  
  if success:
    print("\n" + "="*50)
    print("✓ Installation completed successfully!")
    print("="*50)
    print(f"\nNext steps:")
    print(f"1. Edit {os.path.join(script_path, config_name)}")
    print(f"2. Add your OpenAI API key")
    print(f"3. Log out and log back in, or run {script_name}.exe manually")
  else:
    print("\n⚠ Installation completed with errors.")
    print("Please review the messages above.")
  
  return success

def validate_path(path: str) -> bool:
  """Validate that a path is valid and accessible."""
  try:
    # Check if path is absolute
    if not os.path.isabs(path):
      print(f"✗ Path must be absolute: {path}")
      return False
    
    # Check if parent directory exists or can be created
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
      print(f"✗ Parent directory does not exist: {parent}")
      return False
    
    # Check write permissions
    test_file = os.path.join(parent if parent else path, '.write_test')
    try:
      with open(test_file, 'w') as f:
        f.write('test')
      os.remove(test_file)
    except (PermissionError, OSError):
      print(f"✗ No write permission for: {parent if parent else path}")
      return False
    
    return True
    
  except Exception as e:
    print(f"✗ Invalid path: {e}")
    return False

def validate_name(name: str) -> bool:
  """Validate script name for invalid characters."""
  invalid_chars = '<>:"/\\|?*'
  
  if not name or not name.strip():
    print("✗ Script name cannot be empty")
    return False
  
  if any(char in name for char in invalid_chars):
    print(f"✗ Script name contains invalid characters: {invalid_chars}")
    return False
  
  if len(name) > 50:
    print("✗ Script name is too long (max 50 characters)")
    return False
  
  return True

def menu() -> None:
  """Main menu for installation/uninstallation."""
  print("\n" + "="*50)
  print("       JOKER SETUP - AI Assistant Installer")
  print("="*50)
  
  # Choose operation mode
  print("\nSelect an option:")
  print("  1. Install Joker")
  print("  2. Uninstall Joker")
  print("  3. Exit")
  
  while True:
    choice = input("\nEnter your choice (1-3): ").strip()
    if choice in ('1', '2', '3'):
      break
    print("Invalid choice. Please enter 1, 2, or 3.")
  
  if choice == '3':
    print("Exiting...")
    exit_sys(0)
  
  # Get and validate folder path
  while True:
    folder_path = input("\nEnter installation folder path: ").strip()
    if folder_path and validate_path(folder_path):
      break
    print("Please enter a valid path.")
  
  # Get and validate script name
  while True:
    script_name = input("Enter script name (default: joker): ").strip() or "joker"
    if validate_name(script_name):
      break
    print("Please enter a valid name.")
  
  script_path = os.path.join(folder_path, script_name)
  
  print(f"\nTarget path: {script_path}")

  if choice == '1':
    # Install mode
    if os.path.exists(script_path):
      print("⚠ Installation already exists at this path.")
      if not permission("Overwrite existing installation?"):
        print("Installation cancelled.")
        exit_sys(0)
    
    if permission("\nProceed with installation?"):
      try:
        os.makedirs(script_path, exist_ok=True)
        print(f"✓ Created folder: {script_path}")
        setup(script_path, script_name)
      except Exception as e:
        print(f"✗ Failed to create folder: {e}")
        exit_sys(1)
    else:
      print("Installation cancelled.")
      exit_sys(0)
      
  elif choice == '2':
    # Uninstall mode
    if not os.path.exists(script_path):
      print(f"✗ No installation found at: {script_path}")
      exit_sys(1)
    
    delete_setup(script_path, script_name)

  exit_sys(0)

def main() -> None:
  """Main entry point for the setup script."""
  if not is_admin():
    relaunch_as_admin()
    return
  
  print("\n" + "="*50)
  print("  Running with Administrator privileges")
  print("="*50)
  
  try:
    menu()
  except KeyboardInterrupt:
    print("\n\nSetup interrupted by user.")
    exit_sys(0)
  except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit_sys(1)

if __name__ == "__main__":
  main()

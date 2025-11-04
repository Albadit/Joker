# Joker - AI-Powered Assistant

Joker is an AI-powered desktop assistant that uses OpenAI's GPT models to help answer questions directly from your clipboard. It features hotkey controls, automatic text capture, and a customizable popup display with enable/disable functionality.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Building Executable](#building-executable)
- [Setup Installer](#setup-installer)
- [Task Scheduler Setup](#task-scheduler-setup)
- [Troubleshooting](#troubleshooting)

## Features

- 🤖 **AI-Powered Responses**: Uses OpenAI GPT models (GPT-4, GPT-3.5, etc.) to generate intelligent answers
- ⌨️ **Hotkey Controls**: Quick access with customizable keyboard shortcuts
- 📋 **Clipboard Integration**: Automatically processes copied text
- 🖱️ **Mouse Support**: Right-click to auto-copy selected text (when enabled)
- 🎨 **Customizable UI**: Adjustable window transparency, position, display time, and text wrapping
- 🔒 **Instance Control**: Prevents multiple instances from running simultaneously
- ⏸️ **Toggle Mode**: Enable/disable all functionality on-the-fly with ESC key
- ✅ **Input Validation**: Comprehensive config validation on startup
- 🛠️ **Easy Setup**: Automated installer with Task Scheduler integration
- 📝 **Better Error Handling**: Clear error messages and validation

## Prerequisites

Before installing Joker, ensure you have:

- **Windows OS** (Windows 10 or later recommended)
- **Python 3.8+** installed on your system
- **OpenAI API Key** (get one at [platform.openai.com](https://platform.openai.com))
- **Administrative access** for Task Scheduler setup (optional)

## Installation

### Step 1: Install Python

1. Visit [python.org](https://python.org/downloads/)
2. Download the latest Python 3.x installer for Windows
3. **Important**: Check "Add Python to PATH" during installation
4. Complete the installation wizard

### Step 2: Clone or Download Joker

```bash
git clone https://github.com/yourusername/Joker.git
cd Joker
```

Or download and extract the ZIP file from the repository.

### Step 3: Install Dependencies

You have two options:

**Option A: Using requirements.txt (Recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Manual Installation**
```bash
pip install openai==2.7.1
pip install psutil==7.1.2
pip install pynput==1.8.1
pip install pyperclip==1.11.0
```

**Note**: `configparser` and `tkinter` are included with Python's standard library and don't need separate installation.

## Configuration

1. Open `config.ini` in a text editor
2. Configure the following settings:

```ini
[key]
key_exit = Key.esc      # Toggle enable/disable (ESC key)
key_pop = 1             # Generate AI response (1 key)
key_repop = 2           # Show last response (2 key)

[openai]
api_key = your-api-key-here                    # Your OpenAI API key (REQUIRED)
model = gpt-4                                   # Model to use (gpt-4, gpt-3.5-turbo, etc.)
prompt_system = You are a helpful assistant specialized in answering multiple-choice questions.
prompt_user = Give me only the correct answer and nothing else:

[window]
alpha = 0.5             # Window transparency (0.0-1.0)
display_time = 3000     # Display duration in milliseconds
position = +300+200     # Window position on screen (+X+Y format)
```

**Important Notes:**
- Replace `your-api-key-here` with your actual OpenAI API key
- All configuration keys are validated on startup
- Empty values will cause the program to exit with an error message
- Special keys use format: `Key.esc`, `Key.ctrl`, etc.
- Regular keys use single characters: `1`, `2`, `a`, etc.

## Usage

### Running the Script

```bash
python main.py
```

### Hotkey Controls

- **ESC**: Toggle Joker on/off (disable/enable all functions)
  - When **disabled**: No functions work, right-click doesn't copy
  - When **enabled**: All features are active
  - Status is printed to console
- **1**: Process clipboard text and generate AI response (only when enabled)
- **2**: Display the last generated response (only when enabled)
- **Right-click**: Auto-copy selected text (only when enabled)

### Workflow Example

1. Start Joker (it starts in **enabled** mode)
2. Copy a question to your clipboard (Ctrl+C) or right-click selected text
3. Press **1** to get an AI response
4. A popup window will display the answer for the configured duration
5. Press **2** to see the answer again if needed
6. Press **ESC** to disable Joker temporarily (repeat to re-enable)

## Building Executable

To create a standalone executable using the automated build script:

### Using compile.bat (Recommended)

1. Ensure you're in the project directory
2. Run `compile.bat`
3. The script will:
   - Check Python installation
   - Verify `requirements.txt` exists
   - Install all dependencies automatically
   - Check for UPX compressor (optional but recommended for smaller file sizes)
   - Check for `config.ini` (with warning if missing)
   - Show compilation menu:
     - **1. Main application only** - Compiles only `joker.exe`
     - **2. Setup installer only** - Compiles only `joker_installer.exe`
     - **3. Both** - Compiles both executables
     - **4. Cancel** - Exits without compiling
   - Compile using optimized `.spec` files with size reduction
   - Move executables to the `app` folder
   - Clean up temporary build files
   - Display summary and next steps

**Output:**
- `app/joker.exe` - Main application (~40-80MB without UPX, ~15-30MB with UPX)
- `app/joker_installer.exe` - Setup installer (~10-20MB without UPX, ~3-8MB with UPX)

### Size Optimization

The build process uses optimized `.spec` files that:
- Exclude heavy unnecessary modules (IPython, Jupyter, matplotlib, numpy, pandas, scipy, etc.)
- Only include required dependencies
- Use UPX compression automatically if available
- Main app: ~500MB reduced to ~15-80MB (depending on UPX availability)
- Installer: Minimal size, only includes win32com for Task Scheduler

**To get smaller executables, install UPX:**
1. Download UPX from [https://upx.github.io/](https://upx.github.io/)
2. Extract and add to your system PATH
3. Run `compile.bat` - it will automatically detect and use UPX

### Manual PyInstaller Commands

If you prefer manual compilation, use the optimized `.spec` files:

**Main Application:**
```bash
pyinstaller joker.spec
```

**Setup Installer:**
```bash
pyinstaller joker_installer.spec
```

**Note:** The `.spec` files automatically:
- Include only necessary modules
- Exclude heavy dependencies
- Detect and use UPX if available
- Embed `config.ini` (for main app)
- Apply all optimizations

## Setup Installer

The `joker_installer.exe` provides an easy way to install or uninstall Joker:

### Features

- ✅ **Interactive Menu**: Choose Install, Uninstall, or Exit
- ✅ **Path Validation**: Validates installation paths and permissions
- ✅ **Name Validation**: Checks for invalid characters in script names
- ✅ **Task Scheduler Integration**: Automatically sets up Windows Task Scheduler
- ✅ **Auto-Download**: Downloads the latest executable from GitHub
- ✅ **Config Generation**: Creates default `config.ini` file
- ✅ **Progress Feedback**: Clear step-by-step progress indicators
- ✅ **Error Handling**: Comprehensive error messages and validation

### Using the Installer

1. Run `joker_installer.exe` as Administrator
2. Select option:
   - **1. Install Joker** - Set up new installation
   - **2. Uninstall Joker** - Remove existing installation
   - **3. Exit** - Cancel and exit
3. Enter installation folder path (e.g., `C:\Users\YourName\Documents`)
4. Enter script name (default: `joker`)
5. Confirm to proceed

**Install Mode:**
- Creates installation directory
- Generates `config.ini` with default settings
- Downloads `joker.exe` from GitHub
- Creates Task Scheduler tasks for auto-start:
  - Runs at user login
  - Runs when session unlocks

**Uninstall Mode:**
- Removes Task Scheduler entries
- Deletes installation folder and all files
- Shows confirmation before deletion

## Task Scheduler Setup

Joker can run automatically on Windows startup using Task Scheduler.

### Automatic Setup (via Installer)

The `joker_installer.exe` automatically configures Task Scheduler with optimized settings:
- **Triggers**: Runs at user login and session unlock
- **Privileges**: Runs with highest available privileges
- **Multiple Instances**: Ignores new instances if already running
- **Power Management**: Continues running on battery power

### Manual Setup

To manually set up Task Scheduler:

1. Open **Task Scheduler** (Win + R, type `taskschd.msc`)
2. Click **Action** → **Create Task**
3. **General Tab**:
   - Name: `joker`
   - Check "Run with highest privileges"
4. **Triggers Tab**:
   - Add trigger: "At log on" (specific user)
   - Add trigger: "On workstation unlock" (specific user)
5. **Actions Tab**:
   - Action: Start a program
   - Program: Path to `joker.exe`
   - Start in: Directory containing `joker.exe`
6. **Conditions Tab**:
   - Uncheck "Start only if on AC power"
7. **Settings Tab**:
   - Select "Do not start a new instance"
8. Click **OK** to save

### Alternative: Import XML

If you have a `joker.xml` task definition:

1. Open **Task Scheduler**
2. Click **Action** → **Import Task...**
3. Browse and select `joker.xml`
4. Review settings and click **OK**

## Troubleshooting

### Common Issues

**"Configuration file not found"**
- Make sure `config.ini` is in the same directory as `main.py` or `joker.exe`
- When using the compiled `.exe`, ensure `config.ini` is in the same folder

**"Empty value for 'api_key' in section '[openai]'"**
- Edit `config.ini` and add your OpenAI API key
- Ensure there are no extra spaces or empty values
- All required config keys must have non-empty values

**"OpenAI API Error"**
- Verify your API key is correct in `config.ini`
- Check your internet connection
- Ensure you have API credits available at platform.openai.com
- Check if you're using a compatible model (gpt-4, gpt-3.5-turbo, etc.)

**"ESC key not working"**
- The key format must be `Key.esc` (not just `esc`)
- Check that the key name matches the pynput format
- Special keys: `Key.esc`, `Key.ctrl`, `Key.shift`, etc.
- Regular keys: `1`, `2`, `a`, `b`, etc.

**"Functions not working after pressing 1 or 2"**
- Check if Joker is enabled (press ESC to toggle)
- Console will show "Active" when enabled, "Disabled" when disabled
- Right-click auto-copy also only works when enabled

**"Another instance is already running"**
- Close any existing Joker processes from Task Manager
- Only one instance can run at a time (by design)
- Check Task Scheduler if it's auto-starting

**"Import Error: No module named..."**
- Reinstall dependencies: `pip install -r requirements.txt`
- Ensure you're using the correct Python environment
- For compiled executable, this shouldn't happen

**"Failed to compile with PyInstaller"**
- Ensure all dependencies are installed
- Check that `src\icon.ico` exists
- Ensure `config.ini` exists in the project root
- Try running with administrator privileges

**"Permission denied" during setup/uninstall**
- Run `joker_installer.exe` as Administrator
- Close any running instances of Joker
- Ensure you have write permissions to the target directory

**"Download failed" during installation**
- Check your internet connection
- Verify the GitHub repository is accessible
- You can manually copy `joker.exe` to the installation folder

### OpenAI API Version

This project uses OpenAI API version **1.0.0+** (specifically tested with 2.7.1). The code has been updated to use the new client-based API.

**Key changes from old API (0.28):**
- Uses `OpenAI()` client instantiation
- New syntax: `client.chat.completions.create()`
- Response accessed via attributes, not dictionary keys

If you encounter compatibility issues:

```bash
pip install --upgrade openai
```

## Project Structure

```
Joker/
├── main.py             # Main application script
├── setup.py            # Setup/installer script
├── config.ini          # Configuration file
├── compile.bat         # Automated build script with menu
├── requirements.txt    # Python dependencies
├── joker.spec          # PyInstaller config for main app (optimized)
├── joker_installer.spec # PyInstaller config for installer (optimized)
├── README.md           # This file
├── src/
│   └── icon.ico        # Application icon
├── app/                # Compiled executables (after build)
│   ├── joker.exe
│   └── joker_installer.exe
├── dist/               # Build output (temporary, auto-deleted)
└── build/              # Build cache (temporary, auto-deleted)
```

## Dependencies

Core dependencies (from `requirements.txt`):

- **openai** (2.7.1+) - OpenAI API client for GPT models
- **psutil** (7.1.2+) - Process and system utilities
- **pynput** (1.8.1+) - Keyboard and mouse control
- **pyperclip** (1.11.0+) - Clipboard operations
- **pywin32** (311+) - Windows-specific functionality (for installer)

Development dependencies:
- **pyinstaller** (6.16.0+) - For building standalone executables

Standard library modules (no installation needed):
- `tkinter` - GUI framework
- `configparser` - Configuration file parsing
- `os`, `sys`, `typing` - Core Python modules

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Platform](https://platform.openai.com) - Get API keys and manage credits
- [Python Documentation](https://docs.python.org/3/)
- [pynput Documentation](https://pynput.readthedocs.io/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Task Scheduler Guide](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)

## Recent Updates

### Version 2.0 (November 2024)

**Core Improvements:**
- ✅ Updated to OpenAI API 1.0.0+ (from 0.28)
- ✅ Added comprehensive config validation on startup
- ✅ Improved enable/disable toggle functionality
- ✅ Better error handling throughout the codebase
- ✅ Enhanced UI with text wrapping for long responses
- ✅ Fixed special key detection (Key.esc format)

**Setup Installer Enhancements:**
- ✅ Added interactive menu (Install/Uninstall/Exit)
- ✅ Path and name validation
- ✅ Progress indicators and better feedback
- ✅ Optimized Task Scheduler triggers
- ✅ Download progress and file size display
- ✅ Comprehensive error handling

**Build Script Improvements:**
- ✅ Automated dependency installation via requirements.txt
- ✅ Compilation menu (main/installer/both/cancel options)
- ✅ UPX compression detection and automatic usage
- ✅ Optimized .spec files for 97% size reduction
- ✅ Step-by-step progress indicators
- ✅ Config file validation before build
- ✅ Better error messages and exit codes
- ✅ Automatic cleanup of temporary files
- ✅ Summary output with next steps

**Size Optimization:**
- ✅ Reduced executable size from 500MB to 15-80MB
- ✅ Created optimized .spec files with module exclusions
- ✅ Automatic UPX detection and compression
- ✅ Excluded IPython, Jupyter, matplotlib, numpy, pandas, scipy, and other heavy dependencies
- ✅ Main app: ~15-30MB with UPX, ~40-80MB without
- ✅ Installer: ~3-8MB with UPX, ~10-20MB without

**Code Quality:**
- ✅ Full type hints and docstrings
- ✅ Consistent error handling patterns
- ✅ Better variable naming and organization
- ✅ Removed redundant code
- ✅ Performance optimizations

## Support

If you encounter issues or have questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify all configuration settings in `config.ini`
3. Ensure all dependencies are installed correctly
4. Check console output for error messages
5. Open an issue on GitHub with detailed information

## License

[Add your license information here]

---

**Happy coding and enjoy using Joker! 🃏**
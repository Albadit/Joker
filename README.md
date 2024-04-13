# Setup Joker guide

This guide will walk you through the process of setup Joker on your system. This tools are commonly used for developing modern applications projects.

## Table of Contents
- [Installing Python](#installing-python)
- [Setup Joker](#setup-joker)

## Installing Python

Before installing Python, ensure that your Windows operating system is up to date and that you have administrative access to your machine.

### Downloading Python

1. Visit the official Python website at [python.org](https://python.org/).

2. Hover over the "Downloads" menu, and a dropdown will appear.

3. Click on "Windows".

4. Under "Stable Releases", find the latest version of Python 3.x.x (where x.x is the sub-version number). download the latest stable version available.

5. Click on the link to download the Windows installer executable for the latest Python 3 release.

6. Choose between the 32-bit and 64-bit versions based on your version of Windows. If you are unsure which version to choose, right-click on 'This PC' or 'My Computer' on your desktop or File Explorer, and select 'Properties' to see your system type.


### Additional Packages Installation
<ul>
After installing Python, you may need additional packages for your specific project. `pyperclip`, `keyboard`, `openai` and `psutil` are common packages that you may find useful. Here's how to install them on Windows.

#### Installing pyperclip, keyboard, and openai

With `pip` installed, you can install the `pyperclip`, `pynput`, `openai` and `psutil` packages using the following commands in your Command Prompt:

```
pip install configparser
pip install pyperclip
pip install pynput
pip install openai==0.28
pip install psutil
```
</ul>

## Setup Joker

After successfully installing Python on your machine, follow these steps to compile your code and schedule tasks using `joker.xml`.

### Run the Compile Script

1. Navigate to the directory containing the `compile.bat` file.
2. Double-click on `compile.bat` or open a command prompt in the same directory and type `compile.bat` to run the script.
3. When prompted, press the `Y` key to confirm execution of the script.
4. Wait for the script to complete its tasks.

### Import Task to Scheduler

1. Open Task Scheduler on your computer.
2. In the Action menu, select `Import Task...`.
3. Browse to the location of your `joker.xml` file.
4. Select the file and click `Open` to import it into Task Scheduler.

Ensure that you check the task settings and configure them as necessary to suit your scheduling requirements.

## Conclusion

By following the steps outlined in this guide, you should now have Python installed on your system. These tools are essential for modern development and will help you build powerful and efficient web applications.

Remember to explore the official documentation of each tool to learn more about their capabilities, best practices, and advanced features:

- [Python Documentation](https://docs.python.org/3/)
- [Task Scheduler Documentation](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)

If you encounter any issues or have questions, feel free to consult online forums, communities, or the documentation specific to each tool.

Happy coding and enjoy building amazing applications with Joker!

import os
import platform
import subprocess

def open_terminal_windows(command1, command2):
    if platform.system() == "Windows":
        # Open two cmd windows and run the commands
        subprocess.Popen(["start", "cmd", "/k", command1], shell=True)
        subprocess.Popen(["start", "cmd", "/k", command2], shell=True)
        # The original window will be closed by the batch file (no need for exit() here)

    else:
        # For Linux/Mac, open two terminal windows and run the commands, then close the current one
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command1}; exec bash'], shell=False)
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command2}; exec bash'], shell=False)

def main():
    # Define the commands to be executed
    command1 = "mitmproxy -s mitmproxyserver.py --listen-host 192.168.1.25 --listen-port 7086"
    command2 = "python stream_link_server.py"

    # Check the operating system and open windows accordingly
    os_name = platform.system()
    
    if os_name == "Windows":
        print("Running on Windows...")
        open_terminal_windows(command1, command2)
    elif os_name in ["Linux", "Darwin"]:  # Darwin is macOS
        print("Running on Linux/Mac...")
        open_terminal_windows(command1, command2)
    else:
        print(f"Unsupported OS: {os_name}")

if __name__ == "__main__":
    main()

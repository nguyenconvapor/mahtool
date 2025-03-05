import subprocess
import time
import sys

print(f'Python Script Run & Auto Restart With Custom Time')
print(f'')
print(f'Make Sure Target Script Have Same Folder')
target_script = str('autoproxyremove.py')
restart_time = int('120')

def run_script():
    """Function to run target_script.py."""
    try:
        # Start target_script.py
        process = subprocess.Popen([sys.executable, target_script])
        print(f"Started {target_script} with PID:", process.pid)
        return process
    except Exception as e:
        print(f"Error running {target_script} : {e}")
        return None

def main():
    while True:
        # Run the script
        process = run_script()
        if process:
            try:
                # Wait for 5 minutes (300 seconds)
                time.sleep(restart_time*60)
            finally:
                # After 5 minutes, terminate the running script and restart
                print(f"Terminating {target_script} after minutes.")
                process.terminate()
                process.wait()  # Ensure the process is properly closed
        else:
            print("Failed to start the script, retrying...")
            time.sleep(10)  # Wait before retrying to run the script

if __name__ == "__main__":
    main()

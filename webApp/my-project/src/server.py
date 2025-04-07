import os
import subprocess
import sys
from flask import Flask, jsonify

app = Flask(__name__)

# Global dictionary to track the running scanner processes.
processes = {}

# Folder where your scanner files are located.
SCRIPTS_DIR = os.path.join(os.getcwd(), "scripts")
print("SCRIPTS_DIR set to:", SCRIPTS_DIR)

def start_scanner(scanner_name):
    """
    Checks if a scanner is already running; if so, returns a success message.
    Otherwise, terminates any other scanner process (if you want only one at a time)
    and launches the requested scanner.
    """
    # If the requested scanner is already running, do nothing.
    if scanner_name in processes:
        proc = processes[scanner_name]
        if proc.poll() is None:
            print(f"start_scanner: Scanner '{scanner_name}' is already running.")
            return True, f"{scanner_name} scanner already running."

    # Optionally, terminate any other scanner (only one active at a time)
    for name, proc in processes.items():
        if proc is not None:
            try:
                print(f"start_scanner: Terminating existing process '{name}'...")
                proc.terminate()
                proc.wait(timeout=5)
                print(f"start_scanner: Process '{name}' terminated.")
            except Exception as e:
                print(f"start_scanner: Error terminating process '{name}': {e}")
    processes.clear()

    script_path = os.path.join(SCRIPTS_DIR, f"{scanner_name}.py")
    if not os.path.exists(script_path):
        error_msg = f"Script {scanner_name}.py not found in {SCRIPTS_DIR}."
        print("start_scanner:", error_msg)
        return False, error_msg
    try:
        print(f"start_scanner: Launching {scanner_name}.py using interpreter {sys.executable}...")
        proc = subprocess.Popen([sys.executable, script_path])
        processes[scanner_name] = proc
        success_msg = f"{scanner_name} scanner launched."
        print("start_scanner:", success_msg)
        return True, success_msg
    except Exception as e:
        error_msg = f"Error launching {scanner_name}.py: {e}"
        print("start_scanner:", error_msg)
        return False, error_msg

@app.route("/lifestyle", methods=["GET"])
def run_lifestyle():
    success, message = start_scanner("lifestyle")
    if success:
        return jsonify({"status": message})
    else:
        return jsonify({"error": message}), 500

@app.route("/grocery", methods=["GET"])
def run_grocery():
    success, message = start_scanner("grocery")
    if success:
        return jsonify({"status": message})
    else:
        return jsonify({"error": message}), 500

@app.route("/object-detection", methods=["GET"])
def run_object_detection():
    success, message = start_scanner("object_detection")
    if success:
        return jsonify({"status": message})
    else:
        return jsonify({"error": message}), 500

# The /food endpoint is not available.
# @app.route("/food", methods=["GET"])
# def run_food():
#     return jsonify({"status": "Food processing not available."}), 404

if __name__ == "__main__":
    print("Starting Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)

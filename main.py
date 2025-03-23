import os
import uuid
import subprocess
import boto3
import requests
import time
import json
import signal
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_CREDENTIALS_ACCESS_KEY = os.getenv("AWS_CREDENTIALS_ACCESS_KEY")
AWS_CREDENTIALS_SECRET_KEY = os.getenv("AWS_CREDENTIALS_SECRET_KEY")
AWS_SQS_URL = os.getenv("AWS_SQS_URL")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

sqs = boto3.client(
    "sqs",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_CREDENTIALS_ACCESS_KEY,
    aws_secret_access_key=AWS_CREDENTIALS_SECRET_KEY
)
QUEUE_URL = AWS_SQS_URL

stop_signal = False

def handle_exit(signum, frame):
    global stop_signal
    print("exiting...")
    stop_signal = True

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def download_file(url, save_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(response.content)

def process_task(task):
    try:
        task_data = json.loads(task["Body"])
        file_id = str(uuid.uuid4())
        blend_path = os.path.join(UPLOAD_DIR, f"{file_id}.blend")

        download_file(task_data["rawFileUrl"], blend_path)

        output_base = os.path.join(OUTPUT_DIR, f"{file_id}_output")

        render_command = [
            "blender", "-b", blend_path,
            "--python-expr",
            f"import bpy; bpy.context.scene.render.engine = 'CYCLES'; "
            f"bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'; "
            f"for device in bpy.context.preferences.addons['cycles'].preferences.get_devices(): device.use = True; "
            f"bpy.context.scene.render.resolution_x = {task_data['renderResolutionWidth']}; "
            f"bpy.context.scene.render.resolution_y = {task_data['renderResolutionHeight']}; "
            f"bpy.context.scene.render.resolution_percentage = {task_data['renderResolutionPercentage']}; ",
            "-o", output_base,
            "-F", "PNG", "-x", "1",
        ]

        if task_data["taskType"] == "image":
            render_command += ["-f", str(task_data["frameToRender"])]

        elif task_data["taskType"] == "anim":
            render_command += ["-s", str(task_data["frameStart"]), "-e", str(task_data["frameEnd"]), "-a"]

        process = subprocess.Popen(render_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while process.poll() is None:
            if stop_signal:
                process.terminate()
                print("Rendering aborted.")
                return
            time.sleep(1)

        if process.returncode != 0:
            print("Blender rendering failed:", process.stderr.read().decode())

        print("Rendering complete for task:", task_data)

    except Exception as e:
        print("Error processing task:", str(e))

def poll_sqs():
    while not stop_signal:
        try:
            print("Polling for messages..")
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
                MessageAttributeNames=["All"],
            )

            messages = response.get("Messages", [])

            for message in messages:
                if stop_signal:
                    break
                process_task(message)
                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=message["ReceiptHandle"])

            time.sleep(1)

        except Exception as e:
            print("Error during polling:", str(e))
            break

if __name__ == "__main__":
    print("Worker is listening...")
    poll_sqs()

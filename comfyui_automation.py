import json
import urllib.request
import urllib.parse
import websocket
import uuid
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

COMFYUI_ADDRESS = os.getenv("COMFYUI_ADDRESS", "127.0.0.1:8188")

class ComfyUIAutomation:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")

    def queue_prompt(self, prompt):
        """Sends the workflow prompt to the ComfyUI queue."""
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename, subfolder, folder_type):
        """Downloads a generated image from the ComfyUI server."""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def get_images(self, prompt_id):
        """Listens to the WebSocket for completion and fetches images."""
        output_images = {}
        while True:
            out = self.ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break # Execution is done
            else:
                continue # Preview images are binary, ignore them

        # Fetch history to get output filenames
        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                    output_images[image['filename']] = image_data
        return output_images

    def get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def run_batch_generation(self, workflow_file, prompts_list, output_dir="outputs"):
        """Loads a workflow, updates the prompt, and generates images for a list of text prompts."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # IMPORTANT: You must find the ID of your 'CLIP Text Encode (Prompt)' node in your JSON.
      # Usually it is node "6" (or "2" in this workflow) for the positive prompt..
        POSITIVE_PROMPT_NODE_ID = "2" 

        for i, prompt_text in enumerate(prompts_list):
            print(f"[DataForge Engine] Processing prompt {i+1}/{len(prompts_list)}: {prompt_text[:50]}...")
            
            # Inject the new prompt into the workflow
            workflow[POSITIVE_PROMPT_NODE_ID]["inputs"]["text"] = prompt_text

            # Queue and execute
            prompt_id = self.queue_prompt(workflow)['prompt_id']
            images = self.get_images(prompt_id)

            # Save images
            for filename, image_data in images.items():
                save_path = os.path.join(output_dir, f"batch_{i+1}_{filename}")
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                print(f"[DataForge Engine] Saved: {save_path}")

        print("[DataForge Engine] Batch generation complete!")
        self.ws.close()

if __name__ == "__main__":
    # --- CONFIGURATION ---
    WORKFLOW_FILE = "workflow_api.json" # Your exported ComfyUI API workflow
    
    # The list of prompts you want to automate (could be loaded from a CSV)
    PROMPTS = [
        "a cyberpunk city street at night, neon lights, highly detailed, 8k",
        "a serene japanese garden in spring, cherry blossoms, photorealistic",
        "a futuristic robot reading a book in a cozy library, cinematic lighting"
    ]

    # --- EXECUTION ---
    engine = ComfyUIAutomation(COMFYUI_ADDRESS)
    engine.run_batch_generation(WORKFLOW_FILE, PROMPTS)
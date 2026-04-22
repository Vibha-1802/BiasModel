import os
import requests
import json
import shutil
import time
import argparse

def process_files(preprocess_dir, postprocess_dir, api_url, mode):
    if not os.path.exists(preprocess_dir):
        print(f"Directory {preprocess_dir} not found.")
        return

    # Get all files except .gitkeep
    files = [f for f in os.listdir(preprocess_dir) if f != ".gitkeep"]
    
    if not files:
        print(f"No files to process in {preprocess_dir} folder.")
        return

    # Construct URL with mode parameter
    if "?" in api_url:
        final_url = f"{api_url}&response_mode={mode}"
    else:
        final_url = f"{api_url}?response_mode={mode}"

    # Wait for API to be ready
    print(f"Checking if API is available at {api_url}...")
    for i in range(10):
        try:
            # Check base URL health
            base_url = "/".join(api_url.split("/")[:3])
            requests.get(base_url, timeout=2)
            print("API is ready.")
            break
        except Exception:
            print(f"Waiting for API (attempt {i+1}/10)...")
            time.sleep(2)
    else:
        print("API did not start in time. Exiting.")
        return

    for filename in files:
        filepath = os.path.join(preprocess_dir, filename)
        if not os.path.isfile(filepath):
            continue
            
        print(f"Processing {filename} (Mode: {mode})...")
        
        try:
            with open(filepath, "rb") as f:
                # Note: We use the final_url which includes the response_mode
                response = requests.post(final_url, files={"file": f})
            
            if response.status_code == 200:
                result = response.json()
                
                # Ensure postprocess dir exists
                os.makedirs(postprocess_dir, exist_ok=True)
                
                # Save analysis result
                result_filename = f"{os.path.splitext(filename)[0]}_results.json"
                result_path = os.path.join(postprocess_dir, result_filename)
                
                with open(result_path, "w") as rf:
                    json.dump(result, rf, indent=4)
                
                print(f"Analysis saved to {result_path}")
                
                # Move original dataset to post-processed folder
                dest_path = os.path.join(postprocess_dir, filename)
                shutil.move(filepath, dest_path)
                print(f"Moved {filename} to {postprocess_dir}")
            else:
                print(f"Error processing {filename}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process datasets via Bias Detection API")
    parser.add_argument("--preprocess", default="data/preprocess_data", help="Path to preprocess folder")
    parser.add_argument("--postprocess", default="data/post_processed_data", help="Path to post-processed folder")
    parser.add_argument("--api", default="http://127.0.0.1:8000/bias/analyze-dataset", help="API URL")
    parser.add_argument("--mode", default="full", choices=["summary", "full"], help="Response mode (summary or full)")
    
    args = parser.parse_args()
    
    process_files(args.preprocess, args.postprocess, args.api, args.mode)

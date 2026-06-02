import os
import sys
import logging

# Add app to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.api.events import background_video_processing

# Set up logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    db = SessionLocal()
    video_path = "/data/videos/cctv_footage.mp4"
    layout_path = "/data/uploads/store_layout.xlsx"
    
    if not os.path.exists(layout_path):
        # Look in workspace
        search_dir = "/app"
        for f in os.listdir(search_dir):
            if f.endswith(".xlsx"):
                layout_path = os.path.join(search_dir, f)
                break

    print(f"Starting retail intelligence pipeline on: {video_path}")
    print(f"Layout file: {layout_path}")
    
    try:
        background_video_processing(video_path, layout_path, db)
        print("Pipeline execution completed successfully!")
    except Exception as e:
        print(f"Pipeline error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

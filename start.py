import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

from run_web import open_browser

if __name__ == "__main__":
    import threading
    import uvicorn

    print("洛克王国本地模拟器: http://localhost:8765/dex")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("src.server:app", host="0.0.0.0", port=8765, log_level="warning")

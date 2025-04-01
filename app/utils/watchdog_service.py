import os
import signal
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            file_ext = os.path.splitext(event.src_path)[1].lower()
            if file_ext in ['.py', '.html', '.css', '.js']:
                print(f"\n🔄 Cambio detectado en: {os.path.basename(event.src_path)}")
                print("⚡ Reiniciando servidor...")
                os.kill(os.getpid(), signal.SIGTERM)

def start_watchdog():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def init_watchdog():
    threading.Thread(target=start_watchdog, daemon=True).start()
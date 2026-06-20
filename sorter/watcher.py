import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .rules import RuleEngine
from .mover import is_file_ready, safe_move

class SortHandler(FileSystemEventHandler):
    def __init__(self, rule_engine: RuleEngine):
        self.rules = rule_engine

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process_file(event.dest_path)

    def process_file(self, file_path: str):
        # Stop infinite loops if destination is inside the watch folder
        from pathlib import Path
        try:
            path_obj = Path(file_path).resolve()
            
            # Check if the file is inside any of the category subfolders
            for category in self.rules.rules.keys():
                raw_dest = self.rules.destinations.get(category)
                if raw_dest:
                    dest_dir = (self.rules.make_universal_path(raw_dest) / category).resolve()
                    if dest_dir in path_obj.parents or path_obj == dest_dir:
                        return

            # Check if inside fallback Others subfolder
            others_raw = self.rules.destinations.get('Others')
            if others_raw:
                others_dir = (self.rules.make_universal_path(others_raw) / "Others").resolve()
                if others_dir in path_obj.parents or path_obj == others_dir:
                    return
            else:
                others_dir = (self.rules.watch_dir / "Others").resolve()
                if others_dir in path_obj.parents or path_obj == others_dir:
                    return
        except Exception as e:
            logging.error(f"Loop prevention check error: {e}")

        if is_file_ready(file_path, self.rules.settle_time):
            dest = self.rules.resolve_destination(file_path)
            safe_move(Path(file_path), dest)

class SentinelWatcher:
    def __init__(self, config_path: str):
        self.rules = RuleEngine(config_path)
        self.observer = Observer()

    def start(self):
        handler = SortHandler(self.rules)
        self.observer.schedule(handler, str(self.rules.watch_dir), recursive=False)
        self.observer.start()
        logging.info(f"Sentinel started watching: {self.rules.watch_dir}")
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
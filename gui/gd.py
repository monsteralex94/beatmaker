from .song import Song

class GlobalData:
    def __init__(self) -> None:
        self.song = Song()
        self.current_pattern_number = 0

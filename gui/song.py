import json

START_SAMPLES = 1
START_PATTERNS = 1
START_PATTERN_LENGTH = 1
START_SONG_LENGTH = 1
START_TEMPO = 140.0


class SequencedSample(dict):
    def __init__(self, length_bars: int) -> None:
        super().__init__()
        self['name'] = ''
        self['sequence'] = [False for _ in range(16*length_bars)]


class Pattern(dict):
    def __init__(self, length_bars: int = START_PATTERN_LENGTH, samples: int = START_SAMPLES) -> None:
        super().__init__()
        self['length_bars'] = length_bars
        self['sequenced_samples'] = [SequencedSample(length_bars) for _ in range(samples)]


class Song(dict):
    def __init__(self) -> None:
        super().__init__()
        self['tempo'] = START_TEMPO
        self['length_bars'] = START_SONG_LENGTH
        self['patterns'] = [Pattern() for _ in range(START_PATTERNS)]
        self['arrangement'] = [[False] for _ in range(START_PATTERNS)]


def encode_json(data: Song) -> str:
    return json.dumps(data)

def decode_json(data: str) -> Song:
    return json.loads(data)

import pygame

_sounds: dict = {}


def load():
    """Call once after pygame.init()."""
    specs = {
        "shoot":        ("sounds/shoot.ogg",        0.4),
        "shoot_spread": ("sounds/shoot_spread.ogg",  0.35),
        "laser_beam":   ("sounds/laser_beam.ogg",    0.3),
        "explosion":    ("sounds/explosion.ogg",     0.6),
        "bomb":         ("sounds/bomb.ogg",          0.8),
    }
    for name, (path, volume) in specs.items():
        snd = pygame.mixer.Sound(path)
        snd.set_volume(volume)
        _sounds[name] = snd


def play(name: str):
    if name in _sounds:
        _sounds[name].play()


def loop(name: str):
    """Start looping a sound. Safe to call every frame — won't restart if already playing."""
    if name in _sounds:
        snd = _sounds[name]
        if snd.get_num_channels() == 0:
            snd.play(-1)


def stop(name: str):
    if name in _sounds:
        _sounds[name].stop()

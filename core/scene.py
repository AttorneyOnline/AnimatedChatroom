from collections import deque, OrderedDict
from pyglet.sprite import Sprite

class Scene:

    def __init__(self):
        """
        Initializes a scene.
        """
        self.action_queue = deque()
        # Layers are drawn from bottom to top.
        # String defines a name for the layer (e.g. `background`).
        self.layers = OrderedDict()

    def draw(self):
        for name, layer in self.layers.items():
            layer.draw()
import pyglet
pyglet.options['debug_media'] = True
pyglet.options['debug_lib'] = True
from PyQt5.QtCore import QSize
from ui.qpygletwidget import QPygletWidget
from pyglet import gl
import core.asset
from core.scene import Scene
import core.pylget_loader


class Display(QPygletWidget):

    def on_init(self):
        #res = pyglet.media.load("R:/adachi.webm")
        #animation = pyglet.image.load_animation("adachi.gif")
        #animation = res.get_animation()
        #bin = pyglet.image.atlas.TextureBin()
        #animation.add_to_texture_bin(bin)
        #self.sprite = pyglet.sprite.Sprite(animation)
        #self.sprite.base_width = self.sprite.width
        #self.sprite.base_height = self.sprite.height

        #self.player = pyglet.media.Player()
        #self.player.queue(res)
        #self.player.on_player_next_source = lambda: self.player.queue(res)
        #self.player.loop = True
        #self.player.play()
        char = core.asset.Character('123456')
        char.load()
        self.scene = Scene()
        char._open_tars()
        print(char.content_tars)
        self.scene.layers['background'] = core.pylget_loader.load_animation(char.emotes[0].idle, char.content_tars[char.files[char.emotes[0].idle.filename]])
        char._close_tars()

        self.label = pyglet.text.Label(
            text="This is a pyglet label rendered in a Qt widget :)",
            x = self.width() / 2, y = self.height() / 2, anchor_x='center',
            anchor_y='center')
        self.base_width = 256
        self.base_height = 192
        self.setMinimumSize(QSize(256, 192))
        #self.setMaximumSize(QSize(256, 192))
        self.enable_alpha()

    def on_draw(self):
        pyglet.app.event_loop.idle()
        self.label.draw()
        self.scene.draw()
        #self.player.texture.blit(0, 0, width=self.base_width, height=self.base_height)
        #self.sprite.draw()

    def on_resize(self, w, h):
        super().on_resize(w, h)
        self.label.x = w / 2
        self.label.y = h / 2
        scale = min(w // self.base_width, h // self.base_height)
        gl.glLoadIdentity()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glScalef(scale, scale, scale)

    def enable_alpha(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
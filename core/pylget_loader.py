from .asset import Animation
import pyglet
import pyglet.sprite
import tarfile


def load_animation(animation: Animation, archive: tarfile.TarFile) -> pyglet.sprite.Sprite:
    """
    Loads an animation to a Pyglet sprite.
    `archive` may refer to a tar file which the animation may be located in.
    If this is not the case, then the animation's filename will be used as
    an absolute path."""
    filename = animation.filename
    if archive is not None:
        with archive.extractfile(filename) as f:
            anim = pyglet.image.load_animation(filename, file=f)
    else:
        anim = pyglet.image.load_animation(filename)
    tex_bin = pyglet.image.atlas.TextureBin()
    anim.add_to_texture_bin(tex_bin)
    return pyglet.sprite.Sprite(anim)
import hashlib
import os
import tarfile

from .exceptions import BadHashError, MissingEntryError
import msgpack


class Asset:
    category = ''

    def __init__(self, id: str):
        """Load asset information by ID."""
        self.id = id
        self.path = os.path.join(os.getcwd(), 'assets', self.category, id)
        self.info_path = os.path.join(self.path, 'info.mp')
        self.content_tar_path = os.path.join(self.path, 'content.tar')
        self.content_tar_paths = [self.content_tar_path]
        self.content_tars = None

        # Load asset info
        with open(self.info_path, 'rb') as info_json:
            self.info = msgpack.unpackb(info_json.read(), encoding='utf-8')

        # Recursive: get parent data
        # Can result in an infinite loop
        try:
            self.parent = self.__class__(self.info['parent'])
            self.files = self.parent.files
            self.content_tar_paths += self.parent.content_tar_paths
            del self.parent
        except KeyError:
            # Create a dictionary mapping of paths to tar paths
            self.files = dict()

        # Read once to verify hash
        # Future: self.info.hash_type might indicate something other than sha1
        hasher = hashlib.sha1()
        with open(self.content_tar_path, 'rb') as archive:
            hasher.update(archive.read())
        checksum = hasher.digest()
        if checksum != bytearray.fromhex(self.info['hash']):
            raise BadHashError()

        # Read again to get the files
        with tarfile.open(self.content_tar_path, 'r:*') as archive:
            for f in archive.getmembers():
                if f.isfile():
                    self.files[f.name] = self.content_tar_path

    def load(self):
        """
        Load an asset's resources for in-game use.
        This should be handled by child asset formats.
        """

    def _open_tars(self):
        """Open all content tars from the whole hierarchy."""
        self.content_tars = dict()
        for path in self.content_tar_paths:
            self.content_tars[path] = tarfile.open(path, 'r:*')

    def _close_tars(self):
        """Close all tars opened in _open_tars."""
        for path, archive in self.content_tars.items():
            archive.close()
        self.content_tars = None

    def _unpack_manifest(self):
        """Unpack the manifest."""
        with self.content_tars[self.files['manifest.mp']].extractfile('manifest.mp') as manifest:
            self.manifest = msgpack.unpackb(manifest.read(), encoding='utf-8')

    def __hash__(self):
        return id.__hash__()


class Character(Asset):
    category = 'character'

    def load(self):
        try:
            self._open_tars()
            self._unpack_manifest()

            # Parse the important parts of the manifest
            try:
                self.parse_animations()
                self.parse_emotes()
                self.parse_preanims()
            except KeyError:
                raise MissingEntryError()
        finally:
            self._close_tars()


    def parse_animations(self):
        """Parse animations."""
        self.animations = dict()
        for name, anim in self.manifest['animations'].items():
            stored_anim = Animation()
            stored_anim.filename = anim
            self.animations[name] = stored_anim

    def parse_emotes(self):
        """Parse emotes."""
        self.emotes = []
        for emote in self.manifest['emotes']:
            stored_emote = Emote()
            stored_emote.name = emote['name']
            stored_emote.idle = self.animations[emote['idle']]
            stored_emote.talking = self.animations[emote['talking']]
            if 'talking_preanim' in emote:
                stored_emote.talking_preanim = self.animations[emote['talking_preanim']]
            if 'talking_postanim' in emote:
                stored_emote.talking_postanim = self.animations[emote['talking_postanim']]
            self.emotes.append(stored_emote)

    def parse_preanims(self):
        """Parse preanimations."""
        self.preanims = []
        if 'preanims' not in self.manifest: return
        for preanim in self.manifest['preanims']:
            stored_preanim = Preanimation()
            stored_preanim.name = preanim['name']
            stored_preanim.animation = self.animations[preanim['animation']]
            self.preanims.append(preanim)


class Background(Asset):
    category = 'background'

    def load(self):
        try:
            self._open_tars()
            self._unpack_manifest()

            try:
                self.parse_sides()
                self.parse_overlays()
            except KeyError:
                raise MissingEntryError()
        finally:
            self._close_tars()

    def parse_overlays(self):
        self.overlays = []
        for overlay in self.manifest['overlays']:
            stored_overlay = Animation()
            stored_overlay.filename = overlay
            self.overlays.append(stored_overlay)

    def parse_sides(self):
        self.sides = []
        for side in self.manifest['sides']:
            stored_side = Side()
            stored_side.name = side['name']
            stored_side.animation = Animation()
            stored_side.animation.filename = side['animation']
            self.sides.append(stored_side)


class Audio(Asset):
    category = 'audio'

    def load(self):
        try:
            self._open_tars()
            self._unpack_manifest()

            try:
                self.filename = self.manifest['filename']
                self.length = self.manifest['length']
            except KeyError:
                raise MissingEntryError()
        finally:
            self._close_tars()

class Evidence(Asset):
    category = 'ao3/evidence'

    def load(self):
        try:
            self._open_tars()
            self._unpack_manifest()

            try:
                self.images = self.manifest['images']
            except KeyError:
                raise MissingEntryError()
        finally:
            self._close_tars()

class Animation:
    """
    A group of frames and delays that can be loaded into memory
    and played on screen.

    For now, GIF is the only supported format until pyglet's ffmpeg
    processor can be fixed to decode the alpha channel.

    filename:
        Animation source.
    """
    __slots__ = \
        'filename'


class Emote:
    """
    name:
        Non-unique name of the emote
    icon:
        Icon for the button
    idle:
        Animation when not talking
    talking_preanim:
        Forced preanimation before talking
    talking:
        Animation while talking
    talking_postanim:
        Forced postanimation after talking
    """
    __slots__ = \
        'name', \
        'icon', \
        'idle', \
        'talking_preanim', \
        'talking', \
        'talking_postanim'


class Preanimation:
    """
    name:
        Non-unique name of the preanimation
    icon:
        Icon for the button
    animation:
        The animation
    """
    __slots__ = \
        'name', \
        'icon', \
        'animation'

class Side:
    """
    name:
        Non-unique name
    animation:
        The animation
    """
    __slots__ = \
        'name', \
        'animation'
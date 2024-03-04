import logging
import math

import cairo

from cozy.control.artwork_cache import ArtworkCache
from cozy.model.book import Book
from cozy.ext import inject

from gi.repository import Gtk, GObject, Gdk

ALBUM_ART_SIZE = 200
PLAY_BUTTON_ICON_SIZE = Gtk.IconSize.NORMAL
STROKE_WIDTH = 3

log = logging.getLogger("album_element")


@Gtk.Template.from_resource('/com/github/geigi/cozy/album_element.ui')
class AlbumElement(Gtk.Box):
    __gtype_name__ = "AlbumElement"

    artwork_cache: ArtworkCache = inject.attr(ArtworkCache)

    artwork: Gtk.Picture = Gtk.Template.Child()
    book_icon: Gtk.Image = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()
    play_button: Gtk.Button = Gtk.Template.Child()
    progress_drawing_area: Gtk.DrawingArea = Gtk.Template.Child()
    play_button_revealer: Gtk.Revealer = Gtk.Template.Child()

    def __init__(self, book: Book):
        super().__init__()

        self._book: Book = book
        paintable = self.artwork_cache.get_cover_paintable(book, 1, ALBUM_ART_SIZE)

        if paintable:
            self.artwork.set_paintable(paintable)
            self.artwork.set_size_request(ALBUM_ART_SIZE, ALBUM_ART_SIZE)
            self.stack.set_visible_child(self.artwork)
        else:
            self.book_icon.set_from_icon_name("book-open-variant-symbolic")
            self.stack.set_visible_child(self.book_icon)


        self.play_button.connect("clicked", self._on_play_button_press)
        self.progress_drawing_area.set_draw_func(self._draw_progress)

    def set_playing(self, playing: bool):
        if playing:
            self.play_button.set_icon_name("media-playback-pause-symbolic")
        else:
            self.play_button.set_icon_name("media-playback-start-symbolic")

    def _on_play_button_press(self, _):
        self.emit("play-pause-clicked", self._book)

    def _draw_progress(self, area: Gtk.DrawingArea, context: cairo.Context, *_):
        width = area.get_allocated_width()
        height = area.get_allocated_height()
        button_size = self.play_button.get_allocated_width()
        self.radius = (button_size - STROKE_WIDTH) / 2.0

        book_progress = self._book.progress / self._book.duration

        progress_circle_end = book_progress * math.pi * 2.0
        context.arc(width / 2.0, height / 2.0, self.radius, math.pi * -0.5, progress_circle_end - (math.pi * 0.5))
        if book_progress == 1.0:
            context.set_source_rgb(0.2, 0.82, 0.478)
        else:
            context.set_source_rgb(1.0, 1.0, 1.0)
        context.set_line_width(STROKE_WIDTH)
        context.stroke()

    def draw_background(self, area: Gtk.DrawingArea, context: cairo.Context):
        width = area.get_allocated_width()
        height = area.get_allocated_height()

        context.arc(width / 2.0, height / 2.0, self.radius, 0, math.pi * 2.0)
        context.set_source_rgba(0, 0, 0, 1.0)
        context.set_line_width(2)
        context.stroke()

    def update_progress(self):
        self.progress_drawing_area.queue_draw()


GObject.type_register(AlbumElement)
GObject.signal_new('play-pause-clicked', AlbumElement, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT,
                   (GObject.TYPE_PYOBJECT,))

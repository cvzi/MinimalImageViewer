# Tested with Windows 7/8
# Python 2.7,3.3
# PyGI 3.12.2
# GTK 3.0

from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import sys
import os
import math

def humanBytes(x, p = 1, k = 1024):
    if 0 == x:
        return '0 Byte'
    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    i = math.floor(math.log(x) / math.log(k))
    return ('%.' + str(p) + 'f %s') % ((x / math.pow(k, i)) , sizes[int(i)])


class MinimalViewer:

    def __init__(self, filelist, index = 0):

        self.files = filelist
        self.index = index
        self.filename = False

        self.builder = Gtk.Builder()
        self.builder.add_from_string("""<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <requires lib="gtk+" version="2.24"/>
  <!-- interface-naming-policy project-wide -->
  <object class="GtkWindow" id="window1">
    <property name="can_focus">False</property>
    <property name="default_width">600</property>
    <property name="default_height">400</property>
    <child>
      <object class="GtkVBox" id="vbox1">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <child>
          <object class="GtkScrolledWindow" id="scrolledwindow1">
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="hscrollbar_policy">automatic</property>
            <property name="vscrollbar_policy">automatic</property>
            <child>
              <object class="GtkViewport" id="viewport1">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <child>
                  <object class="GtkImage" id="image1">
                    <property name="visible">True</property>
                    <property name="can_focus">False</property>
                    <property name="stock">gtk-missing-image</property>
                  </object>
                </child>
              </object>
            </child>
          </object>
          <packing>
            <property name="expand">True</property>
            <property name="fill">True</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <object class="GtkStatusbar" id="statusbar1">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="spacing">2</property>
            <child>
              <object class="GtkLabel" id="label1">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <property name="label" translatable="yes">label</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="label2">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <property name="label" translatable="yes">label</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">2</property>
              </packing>
            </child>
            <child>
              <object class="GtkLabel" id="label3">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <property name="label" translatable="yes">label</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">2</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="position">1</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>""")

        self.window = self.builder.get_object("window1")

        # Events
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.connect("check_resize", self._on_resize)
        self.window.connect("key-press-event", self._on_key_press)
        self.window.connect('scroll-event', self.scroll_notify_event)
        
        # Image
        self.scrolledwindow1 = self.builder.get_object("scrolledwindow1")
        self.pixbuf = GdkPixbuf.Pixbuf()
        self.image_width = 0
        self.image_height = 0
        self.image_size = 0
        self.image = self.builder.get_object('image1')
        self.image.set_from_stock(Gtk.STOCK_NEW, Gtk.IconSize.DIALOG)
        self.lastResize = None

        # Status
        self.labelFile = self.builder.get_object("label1")
        self.labelFile.set_label("None");
        self.labelSize = self.builder.get_object("label2")
        self.labelSize.set_label("");
        self.labelScale = self.builder.get_object("label3")
        self.labelScale.set_label("");

        self._openImage();

    def _openImage(self):
        try:
            filename = self.files[self.index]
        except IndexError:
            self.labelFile.set_label("No files found")
            self.labelSize.set_label("");
            self.labelScale.set_label("");
            self.filename = False
            return False

        loaded = True
        try:
            self.pixbuf = self.pixbuf.new_from_file(filename)
            self.image_width = self.pixbuf.get_width()
            self.image_height = self.pixbuf.get_height()
            self.image.set_from_pixbuf(self.pixbuf)
            self.image_size = os.stat(filename).st_size
        except:
            loaded = False


        if not loaded:
            self.image.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.DIALOG)
            self.labelFile.set_label("Could not load %s" % filename)
            self.labelSize.set_label("");
            self.labelScale.set_label("");
            self.filename = False
            return False
        else:
            self.labelFile.set_label(filename)
            self.labelSize.set_label("%dx%dpx - %s" % (self.image_width, self.image_height, humanBytes(self.image_size)));
            self.labelScale.set_label("");
            self.filename = filename
            self._on_resize(force=True)
            return True

    def previousImage(self):
        self.index -= 1
        if self.index == -1:
            self.index += len(self.files)
        self._openImage()

    def nextImage(self):
        self.index += 1
        if self.index == len(self.files):
            self.index = 0
        self._openImage()


    def _on_key_press(self, win, ev):
        key = Gdk.keyval_name(ev.keyval)
        if key == 'Left':
            self.previousImage()
            win.emit_stop_by_name("key-press-event")
            return True
        elif key == 'Right':
            self.nextImage()
            win.emit_stop_by_name("key-press-event")
            return True

    def _on_resize(self, window=None, force=False):
        # Check whether a resize is possible/needed
        if not self.filename:
            return

        scrolledAllocation = self.scrolledwindow1.get_allocation()
        if not force and self.lastResize and self.lastResize[0] == scrolledAllocation.width and self.lastResize[1] == scrolledAllocation.height:
            return

        # Scale
        w = float(self.image_width)
        h = float(self.image_height)
        totalscale = 1.0

        if h > scrolledAllocation.height:
            scale = scrolledAllocation.height / h
            w *= scale
            h *= scale
            totalscale *= scale

        if w > scrolledAllocation.width:
            scale = scrolledAllocation.width / w
            w *= scale
            h *= scale
            totalscale *= scale

        w = int(math.floor(w))
        h = int(math.floor(h))
        totalscale = math.ceil(totalscale*100.0)

        # Update image
        if (w != self.image_width or h != self.image_height) and w > 0 and h > 0:
            pixbuf = self.pixbuf.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
            self.image.set_from_pixbuf(pixbuf)
            self.lastResize = [scrolledAllocation.width,scrolledAllocation.height]
            self.labelScale.set_label("%d%%" % totalscale);

    def scroll_notify_event(self, w, e):
        if e.direction == Gdk.ScrollDirection.UP:
           self.nextImage()
        elif e.direction == Gdk.ScrollDirection.DOWN:
           self.nextImage()            
            
def main():
    ext = (".jpg",".gif",".bmp",".tif",".png",".tga",".webp")
    filename = False
    directory = "."
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            filename = sys.argv[1]
            directory = os.path.dirname(sys.argv[1])

        if os.path.isdir(sys.argv[1]):
            directory = sys.argv[1]

    images = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(ext):
                images.append(os.path.abspath(os.path.join(root, file)))
    index = 0
    if filename:
        try:
            index = images.index(os.path.abspath(filename))
        except ValueError:
            pass

    win = MinimalViewer(images,index)
    win.window.show_all()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python MinimalImageViewer.py imagefile.jpg")
        print("       python MinimalImageViewer.py myphotofolder")
        print("Navigate in a directory with the keyboard arrow keys or mouse scroll")
sys.exit(main())

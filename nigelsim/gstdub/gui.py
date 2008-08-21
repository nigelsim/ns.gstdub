import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
import pygst
pygst.require('0.10')
import gst
import gst.interfaces

import nigelsim.gstdub

class VideoWidget(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.imagesink = None
        self.unset_flags(gtk.DOUBLE_BUFFERED)

    def do_expose_event(self, event):
        if self.imagesink:
            self.imagesink.expose()
            return False
        else:
            return True

    def set_sink(self, sink):
        assert self.window.xid
        self.imagesink = sink
        self.imagesink.set_xwindow_id(self.window.xid)
gobject.type_register(VideoWidget)

class MainWindow:
    def __init__(self):
        # Load the glade
        gladefile = nigelsim.gstdub.__file__[:-12] + 'main.glade'
        self.wTree = gtk.glade.XML(gladefile) 
        self.wTree.signal_autoconnect(self)
        self.window = self.wTree.get_widget('MainWindow')
        self.inputFile = self.wTree.get_widget('inputFile')
        self.outputFile = self.wTree.get_widget('outputFile')
        self.window.connect("destroy", gtk.main_quit)

        self.videoWidget = VideoWidget()
        vbox = self.wTree.get_widget('dialog-vbox1')
        vbox.pack_start(self.videoWidget)
        self.videoWidget.show_all()

        self.window.show()

        # Setup the player
        self.playing = False
        self.player = gst.element_factory_make("playbin", "player")

        bus = self.player.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('sync-message::element', self.on_sync_message)
        bus.connect('message', self.on_message)
        self._setup_recorder()

    def _setup_recorder(self):
        s = 'alsasrc ! level message=true ! audioconvert ! wavenc ! filesink'
        self.recorder = gst.parse_launch(s)
        self.output = self.recorder.get_by_name('filesink0')
        self.output.set_property('location','/tmp/output.wav')
        import ipdb; ipdb.set_trace()

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        if message.structure.get_name() == 'prepare-xwindow-id':
            # Sync with the X server before giving the X-id to the sink
            gtk.gdk.display_get_default().sync()
            self.videoWidget.set_sink(message.src)
            message.src.set_property('force-aspect-ratio', True)
            
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            if self.on_eos:
                self.on_eos()
            self.playing = False
        elif t == gst.MESSAGE_EOS:
            if self.on_eos:
                self.on_eos()
            self.playing = False

    def main(self):
        gtk.main()

    def on_cmdStartStop_clicked(self, widget):
        print "Start"
        self.player.set_property('uri', 'file:///home/nigel/test.ogg')
        self.player.set_state(gst.STATE_PLAYING)
        self.recorder.set_state(gst.STATE_PLAYING)

    def on_cmdQuit_clicked(self, widget):
        print "Quit"
        gtk.main_quit()

    def on_eos(self):
        print "End of stream"
        self.recorder.set_state(gst.STATE_PAUSED)
        self.recorder.set_state(gst.STATE_NULL)

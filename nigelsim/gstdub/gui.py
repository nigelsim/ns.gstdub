import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import nigelsim.gstdub

class MainWindow:
    def __init__(self):
        gladefile = nigelsim.gstdub.__file__[:-12] + 'main.glade'
        self.wTree = gtk.glade.XML(gladefile) 
        self.wTree.signal_autoconnect(self)
        self.window = self.wTree.get_widget('MainWindow')
        self.inputFile = self.wTree.get_widget('inputFile')
        self.outputFile = self.wTree.get_widget('outputFile')
        self.window.connect("destroy", gtk.main_quit)
        self.window.show()

    def main(self):
        gtk.main()

    def on_cmdStartStop_clicked(self, widget):
        print "Start"

    def on_cmdQuit_clicked(self, widget):
        print "Quit"
        gtk.main_quit()

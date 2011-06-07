#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet
import gobject
import wnck

import sys
import codecs
import random

# debugging
import os
new_stdout = open ("/tmp/debug.stdout", "w")
new_stderr = open ("/tmp/debug.stderr", "w")
os.dup2(new_stdout.fileno(), sys.stdout.fileno())
os.dup2(new_stderr.fileno(), sys.stderr.fileno())

class AlignedWindow(gtk.Window):

    def __init__(self, widgetToAlignWith):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_decorated(False)
        
        self.widgetToAlignWith = widgetToAlignWith

    def positionWindow(self):
        # Get our own dimensions & position
        self.realize()
        gtk.gdk.flush()
        #print self.window.get_geometry()
        ourWidth  = (self.window.get_geometry())[2]
        ourHeight = (self.window.get_geometry())[3]

	# Skip the taskbar, and the pager, stick and stay on top
	self.stick()
	# not wrapped self.set_skip_taskbar_hint(True)
	# not wrapped self.set_skip_pager_hint(True)
	self.set_type_hint (gtk.gdk.WINDOW_TYPE_HINT_DOCK)

        # Get the dimensions/position of the widgetToAlignWith
        self.widgetToAlignWith.realize()
	entryX, entryY = self.widgetToAlignWith.window.get_origin()
        entryWidth  = (self.widgetToAlignWith.window.get_geometry())[2]
        entryHeight = (self.widgetToAlignWith.window.get_geometry())[3]

        # Get the screen dimensions
        screenHeight = gtk.gdk.screen_height()
        screenWidth = gtk.gdk.screen_width()

        if entryX + ourWidth < screenWidth:
            # Align to the left of the entry
            newX = entryX
        else:
            # Align to the right of the entry
            newX = (entryX + entryWidth) - ourWidth

        if entryY + entryHeight + ourHeight < screenHeight:
            # Align to the bottom of the entry
            newY = entryY + entryHeight
        else:
            newY = entryY - ourHeight

        # -"Coordinates locked in captain."
        # -"Engage."
        self.move(newX, newY)
        self.show()



class WSNameEntryWindow(AlignedWindow):
    def __init__(self, widget, app):
        AlignedWindow.__init__(self, widget)
        self.app = app
	frame = gtk.Frame()
	frame.set_shadow_type(gtk.SHADOW_OUT)
        self.entry = gtk.Entry()
	frame.add(self.entry)
	self.add(frame)
	
	self.set_default_size(0,0)
        self.entry.connect("activate", self._on_activate)
        self.entry.connect("key-release-event", self._on_key_release)

    def _on_activate(self, event):
        self.app.toggle.set_active(False)
        self.app.workspace.change_name(self.entry.get_text())
        
    def _on_key_release(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.app.toggle.set_active(False)

class WSNameApplet(gnomeapplet.Applet):
    _name_change_handler_id = None
    workspace = None
    
    def __init__(self,applet,iid):
        self.width = 130
        self.applet = applet

        self.toggle = gtk.ToggleButton()
	self.toggle.connect("toggled", self._on_toggled)
        self.toggle.connect("button-press-event", self._on_button_press)
	self.label = gtk.Label()
	self.applet.add(self.toggle)
	self.toggle.add(self.label)
	
	self.screen = wnck.screen_get_default()
	self.screen.connect("active_workspace_changed", self._on_workspace_changed)
	self.entry_window = WSNameEntryWindow(self.applet, self)

	self._name_change_handler_id = None


    def _on_toggled(self, event):
        if self.toggle.get_active():
            self.entry_window.positionWindow()            
            self.entry_window.show_all()
            self.entry_window.present()
	    self.entry_window.entry.set_text(self.workspace.get_name())
            self.entry_window.entry.set_position(-1)            
            self.entry_window.entry.select_region(0, -1)
            gobject.timeout_add(0, self.entry_window.entry.grab_focus)
        else:
            self.entry_window.hide()

    def _on_button_press(self, toggle, event):
        if event.button != 1:
            toggle.stop_emission("button-press-event")

    def _on_workspace_changed(self, event, old_workspace):
        if self.toggle.get_active():
            self.toggle.set_active(False)
	if (self._name_change_handler_id):
	    self.workspace.disconnect(self._name_change_handler_id)
        self.workspace = really_get_active_workspace(self.screen)
	self._name_change_handler_id = self.workspace.connect("name-changed", self._on_workspace_name_changed)
        self.show_workspace_name()

    def _on_workspace_name_changed(self, event):
        self.show_workspace_name()

    def show_workspace_name(self):
        self.label.set_text(self.workspace.get_name())
	self.applet.show_all()

def really_get_active_workspace(screen):
    # This bit is needed because wnck is asynchronous.
    while gtk.events_pending():
        gtk.main_iteration() 
    return screen.get_active_workspace()

gobject.type_register(WSNameApplet)

def app_factory(applet,iid):
    return WSNameApplet(applet,iid)

if len(sys.argv) == 2:
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.connect("destroy", gtk.main_quit)
    main_window.set_title("Applet")
    app = gnomeapplet.Applet()
    app_factory(app,None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()


gnomeapplet.bonobo_factory("OAFIID:GNOME_wsname_Factory", WSNameApplet.__gtype__, "ws-name", "0", app_factory)
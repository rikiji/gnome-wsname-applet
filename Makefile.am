serverdir       = $(libdir)/bonobo/servers
libexec_SCRIPTS = wsname.py
server_DATA     = GNOME_wsname.server

wsnamedir = /usr/lib/python2.6/wsname

wsname_PYTHON = 		\
	wsname.py            

pixmapsdir = $(datadir)/pixmaps
pixmaps_DATA = wsname.png

DISTCLEANFILES =                \
	GNOME_wsname.server \
        intltool-extract        \
        intltool-merge          \
        intltool-update         


EXTRA_DIST =  			\
	$(pixmaps_DATA)		\
        intltool-update.in      \
        intltool-extract.in     \
        intltool-merge.in       \
	ws-name.server 

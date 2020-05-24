import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, GtkSource, Gio, GObject
import sys


class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(
            self, title="TextEdit", application=app)

        self.resize(800, 600)

        # a vbox to attach the toolbar, the scrolled_window
        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.BOTH_HORIZ)
        toolbar.set_icon_size(1)

        openbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_OPEN)
        openbutton.set_is_important(True)
        openbutton.set_action_name("app.open")

        savebutton = Gtk.ToolButton(stock_id=Gtk.STOCK_SAVE)
        savebutton.set_is_important(True)
        savebutton.set_action_name("app.save")

        toolbar.insert(openbutton, 0)
        toolbar.insert(savebutton, 1)
        toolbar.set_property("height-request", 10)
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        vbox.pack_start(toolbar, False, False, 0)

        # set header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("TextEdit")
        self.set_titlebar(header)

        # a text buffer (stores text)
        buffer = GtkSource.Buffer()
        buffer.set_text("")

        # a textview (displays the buffer)
        self.view = GtkSource.View(buffer=buffer)
        # wrap the text, if needed, breaking lines in between words
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        # show line numbers
        self.view.set_show_line_numbers(True)

        # the scrolledwindow
        scrolled_window = Gtk.ScrolledWindow()
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        # textview is scrolled
        scrolled_window.add(self.view)

        # add the scrolledwindow to the window
        vbox.pack_end(scrolled_window, True, True, 0)
        self.add(vbox)


class TextEdit(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.win = Window(self)
        self.win.show_all()
        self.file = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # open action
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", self.open_callback)
        app.add_action(open_action)

        # save action
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", self.save_callback)
        app.add_action(save_action)

        # set accelerator
        app.set_accels_for_action("app.save", ("<Primary>S",))

    def open_callback(self, action, parameter):
        open_dialog = Gtk.FileChooserDialog(title="Open a file", parent=None,
                                            action=Gtk.FileChooserAction.OPEN)
        open_dialog.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT)

        response = open_dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            # self.file is the file that we get from the FileChooserDialog
            self.file = open_dialog.get_file()
            # an empty string (provisionally)
            content = ""
            try:
                # load the content of the file into memory:
                # success is a boolean depending on the success of the operation
                # content is self-explanatory
                # etags is an entity tag (can be used to quickly determine if the
                # file has been modified from the version on the file system)
                [success, content, etags] = self.file.load_contents(None)
            except GObject.GError as e:
                print("Error: " + e.message)
            # set the content as the text into the buffer
            self.win.view.get_buffer().set_text(content.decode("utf-8"), len(content))

        open_dialog.destroy()

    def save_callback(self, action, parameter):
        save_dialog = Gtk.FileChooserDialog(title="Save as a file", parent=None,
                                            action=Gtk.FileChooserAction.SAVE)
        save_dialog.add_buttons(Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT)

        save_dialog.set_do_overwrite_confirmation(True)
        response = save_dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            # save the file
            self.file = save_dialog.get_file()
            # if self.file has already been saved
            if self.file is not None:
                try:
                    # set self.file as the current filename for the file chooser
                    self.save_to_file()
                except GObject.GError as e:
                    print("Error: " + e.message)

        save_dialog.destroy()

    # save_to_file
    def save_to_file(self):
        # get the content of the buffer, without hidden characters
        [start, end] = self.win.view.get_buffer().get_bounds()
        current_contents = self.win.view.get_buffer().get_text(start, end, False)
        # if there is some content
        if current_contents != "":
            # set the content as content of self.file.
            # arguments: contents, etags, make_backup, flags, GError
            try:
                self.file.replace_contents(current_contents.encode(), None,
                                            False, Gio.FileCreateFlags.NONE, None)
            except GObject.GError as e:
                print("Error: " + e.message)
        # if the contents are empty
        else:
            # create (if the file does not exist) or overwrite the file in readwrite mode.
            # arguments: etags, make_backup, flags, GError
            try:
                self.file.replace_readwrite(None, False,
                                            Gio.FileCreateFlags.NONE, None)
            except GObject.GError as e:
                print("Error: " + e.message)

Gtk.init(sys.argv)
app = TextEdit()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
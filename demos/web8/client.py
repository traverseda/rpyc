import rpyc
from efl import elementary
from efl import elementary as elm
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EXPAND_BOTH, EXPAND_HORIZ, FILL_HORIZ, FILL_BOTH
from safeElm import SafeElm

def BrowserServiceFactory(browser):
    class BrowserService(rpyc.Service):
        def on_connect(self):
            pass
#            conn._config["allow_public_attrs"] = True
        def exposed_navigate(self, url):
            old_url = browser.txt_url.get_text()
            if url.startswith("/"):
                base = old_url.split("/")[0]
                url = base + url
            browser.txt_url.set_text(url)
            browser.on_navigate(None)
    return BrowserService

internalPages = {
}

class Browser(elm.StandardWindow):
    def __init__(self,url="browser:home"):
        self.conn = None
        super().__init__("window-states", "Web8 Browser")
        self.callback_delete_request_add(self.on_close)
        # main vertical box
        vbox = elm.Box(self, size_hint_weight=EXPAND_BOTH)
        self.wrapper = vbox
        self.resize_object_add(vbox)
        vbox.show()

        ### Header ###
        hbox1 = elm.Box(vbox, horizontal=True)
        fr = elm.Frame(vbox, style='outdent_bottom', content=hbox1,
                       size_hint_weight=EXPAND_HORIZ,
                       size_hint_align=FILL_HORIZ)
        vbox.pack_end(fr)
        fr.show()

        # search entry
        en = elm.Entry(hbox1, single_line=True, scrollable=True,
                       size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        en.callback_activated_add(self.on_navigate)
        hbox1.pack_start(en)
        en.entry = url
        en.show()
        self.url = en
        #Content frame
        self.box_main = elm.Box(vbox, horizontal=False,
                       size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        vbox.pack_end(self.box_main)
        self.box_main.show()
        self.box_content = None
        self.on_navigate()
#        btn_send = gtk.Button("Go")
#        btn_send.show()
#        btn_send.connect("clicked", self.on_navigate)
#        hbox1.pack_start(btn_send, fill=False, expand=False, padding = 10)

        self.show()

    def on_close(self, widget):
        if self.conn:
            self.conn.close()
            self.conn = None
        elementary.exit()

    def on_navigate(self, data = None):
        if self.box_content:
            self.box_main.clear()
            self.box_content = None
        url = self.url.entry

        #Handle internal urls according to some dict
        if url.startswith("browser:"):
            host=None
            page = url.split(":",1)[1]
            if page in internalPages:
                interalPages[page](self)
            else:
                self.box_content = elm.Label(self.box_main,
                    text="Could not find internal page named '{}'\n Options are '{}'".format(page, ", ".join(internalPages.keys())))
                self.box_content.show()
                self.box_main.pack_start(self.box_content)
            return

        if "/" not in url:
            url += "/"
        host, page = url.split("/", 1)
        if ":" in host:
            addr, port = host.split(":", 1)
            port = int(port)
        else:
            addr = host
            port = 18833

        if self.conn:
            self.conn.close()
            self.conn = None
        self.box_content = elm.Box(self.wrapper, horizontal=False,
                       size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.box_content.show()
        self.box_main.pack_start(self.box_content)

        self.conn = rpyc.connect(host, port, service = BrowserServiceFactory(self))
#        gobject.io_add_watch(self.conn, gobject.IO_IN, self.bg_server)
        try:
            self.conn.root.get_page(SafeElm, self.box_content, page)
        except Exception as e:
            self.box_content = elm.Entry(self.box_main,
                    text=str(e), size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH,
                    file_text_format=elm.ELM_TEXT_FORMAT_MARKUP_UTF8,
                )
            self.box_content.show()
            self.box_main.pack_start(self.box_content)


    def bg_server(self, source = None, cond = None):
        if self.conn:
            self.conn.poll_all()
            return True
        else:
            return False


if __name__ == "__main__":
    b = Browser()
    elementary.run()

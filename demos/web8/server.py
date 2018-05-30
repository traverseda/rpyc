import rpyc
from rpyc.utils.server import OneShotServer as Server
#from rpyc.utils.server import ThreadedServer as Server
import time
import threading
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EXPAND_BOTH, EXPAND_HORIZ, FILL_HORIZ, FILL_BOTH

class Web8Service(rpyc.Service):
    def exposed_get_page(self, elementry, content, page):
        self.elm = elementry #The exposed subset of the elementry toolkit
        self.content = content
        page = page.replace(" ", "_").lower()
        pagefunc = getattr(self, "page_%s" % (page,), None)
        if pagefunc:
            pagefunc()
        else:
            lbl1 = self.elm.Label(self.content,
                                text="Page '{}' does not exist".format(page), size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH,
                          )
            lbl1.show()
            self.content.pack_start(lbl1)

    def page_main(self):
        counter = [0]
        lbl1 = self.elm.Label(self.content,
                            text="Hello mate, this is the main page", size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH,
                      )
        lbl1.show()
        self.content.pack_start(lbl1)

        def on_btn1_clicked(src):
            counter[0] += 1
            lbl2.set_text("You have clicked the button %d times" % (counter[0],))

        btn1 = self.elm.Button("Add 1")
        btn1.connect("clicked", on_btn1_clicked)
        btn1.show()
        self.content.pack_start(btn1)

        lbl2 = self.gtk.Label("You have clicked the button 0 times")
        lbl2.show()
        self.content.pack_start(lbl2)

        def on_btn2_clicked(src):
            self._conn.root.navigate("/hello_world")

        btn2 = self.gtk.Button("Go to the 'hello world' page")
        btn2.connect("clicked", on_btn2_clicked)
        btn2.show()
        self.content.pack_start(btn2)

        active = [False]

        def bg_timer_thread():
            while active[0]:
                rpyc.async(lbl3.set_text)("Server time is: %s" % (time.ctime(),))
                time.sleep(1)

        bg_thread = [None]

        def on_btn3_clicked(src):
            if btn3.get_label() == "Start timer":
                bg_thread[0] = threading.Thread(target = bg_timer_thread)
                active[0] = True
                bg_thread[0].start()
                btn3.set_label("Stop timer")
            else:
                active[0] = False
                bg_thread[0].join()
                btn3.set_label("Start timer")

        btn3 = self.gtk.Button("Start timer")
        btn3.connect("clicked", on_btn3_clicked)
        btn3.show()
        self.content.pack_start(btn3)

        lbl3 = self.gtk.Label("Server time is: ?")
        lbl3.show()
        self.content.pack_start(lbl3)

    def page_hello_world(self):
        lbl = self.elm.Label(self.content,
                    text="Hello World", size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH,
              )

        lbl.show()
        self.content.pack_start(lbl)

if __name__ == "__main__":
    t = Server(Web8Service, port = 18833)
    t.start()


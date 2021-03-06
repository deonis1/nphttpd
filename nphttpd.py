# License: GPL
# GNU GENERAL PUBLIC LICENSE
# Copyright (C) Denis Spasyuk
import socket
from time import sleep
from machine import Pin
from machine import reset
from neopixel import NeoPixel
from network import WLAN, STA_IF

class HttServ(object):
    def __init__(self):
        self.ip_address = '192.168.0.250'  # set your ip here
        ip_change = self.set_ip()
        if ip_change:
           self.port = 80  # set your port here
           pin_id = 5
           nparray = 60
           self.conn = None
           self.s = None
           self.np = NeoPixel(Pin(pin_id), nparray)
           self.run_socket()

    def set_ip(self):
        sta_if = WLAN(STA_IF)
        sta_if.active(True)
        sta_if.ifconfig((self.ip_address,'255.255.255.0','192.168.0.1','192.168.0.1'))
        sleep(1)
        return True

    def connection(self, html):
        try:
            self.conn.sendall(html)
            sleep(0.2)
        except Exception as exc:
            print("Send Error", exc.args[0])
            pass
        finally:
            self.conn.close()

    def parse_request(self):
        self.ledout = self.request.find("rgb(")
        self.ledoff = self.request.find("OFF")
        if self.ledout > -1:
            color = ((self.request[self.ledout:self.ledout+40]).split("%22")[0]).replace("%20", "")
            #print(eval(color.replace("rgb", "")))
            for i, pixel in enumerate(self.np):
                 self.np[i] = eval(color.replace("rgb", ""))
                 self.np.write()
        if self.ledoff > -1:
            for i, pixel in enumerate(self.np):
                 self.np[i] = (0,0,0)
                 self.np.write()
        self.request = None

    def run_socket(self):
        self.request = None
        html = None
        try:
            with open("index.html", "r") as fhtml:
                html = fhtml.read()
        except OSError:
            pass
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind((self.ip_address, self.port))
            self.s.listen(5)
        except Exception as exc:
            print("Address in use, restarting", exc.args[0])
            sleep(2)
            reset()
            pass
        while True:
            try:
                self.conn, addr = self.s.accept()
                for i in str(self.conn).split():
                    print(i)
            except Exception as exc:
                print("Socket Accept Error ", exc.args[0])
                reset()
                pass
            print('Connected by', addr)
            try:
                self.request = str(self.conn.recv(1024))
            except Exception as exc:
                print("recv -------------", exc.args[0])
                reset()
                pass
            #if not self.request: break
            self.parse_request()
            self.connection(html)

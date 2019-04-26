import array
import struct
import sys
import time

import win32con
import win32gui

BAUDRATE = 9600

class ControlSpecLabW32UI(object):
    def __init__(self, inst=1):
        self.inst = inst
        self.hwnd = win32gui.FindWindow("SpecLab%d" % self.inst, None)
##        self.hwnd = win32gui.FindWindow("TSpectrumLab", None)

    def send_command(self, cmd):
        b = array.array('B', bytearray(cmd, "windows-1252"))
        b_addr, b_size = b.buffer_info()
        data = struct.pack("4sLP", b"CLEC", b_size, b_addr)
        return win32gui.SendMessage(self.hwnd, win32con.WM_COPYDATA, None, data)

#==============================================================================#

import serial

class RigEmulator(object):
    def __init__(self, port="COM2", baudrate=9600, inst=1, verbose=False):
        self.inst = inst
        self.speclab = ControlSpecLabW32UI(inst=self.inst)
        self.active_vfo = 0
        self.recv_freq = [False, False]
        self.vfo = [0, 0]
        self.sp = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.buffer = b""
        self.unprocessed = []
        self.ppb = 0
        self.verbose = verbose
        if verbose:
            print("open serial port %s" % self.sp.name)
            if self.speclab.hwnd:
                print("found SpecLab%d at 0x%08X" % (self.inst,
                                                     self.speclab.hwnd))

    def process_FA(self, vfo=0, arg=None):
        # processes incoming FA
        if arg == None:
            return bytes("FA%011d" % self.vfo[vfo], "ansi")
        else:
            if self.verbose:
                if vfo != self.active_vfo:
                    print("activating vfo %s" % "ABCDEFGHI"[vfo])
                if not self.recv_freq[vfo]:
                    print("enabling vfo %s" % "ABCDEFGHI"[vfo])
                print("set vfo %d" % (self.vfo[vfo]*(1+self.ppb/1000000000.)))
            self.active_vfo = vfo
            self.recv_freq[vfo] = True
            self.vfo[vfo] = int(arg)
            self.speclab.send_command("sdr.freq = %d" % \
                                      int(self.vfo[vfo]*\
                                          (1+self.ppb/1000000000.)))

            return self.process_FA()
        
    def process_FB(self, arg=None):
        # processes incoming FA
        if arg == None:
            return bytes("FA%011d" % self.vfo[1], "ansi")
        else: 
            self.active_vfo = 1
            self.vfo[1] = int(arg)
            self.recv_freq[1] = True
            self.speclab.send_command("sdr.freq = %d" % \
                                      int(self.vfo[1]*\
                                          1+(self.ppb/1000000000.)))
            return self.process_FA()

    def run_buffer(self):
        self.buffer += self.sp.read()
        while b';' in self.buffer:
            cmd, _, self.buffer = self.buffer.rpartition(b';')
            self.unprocessed.append(cmd)

    def process_commands(self):
        while self.unprocessed:
            cmd = self.unprocessed.pop(0) # yeah that's bad, get over it
            if len(cmd) < 2: continue
            elif len(cmd) == 2:
                arg = None
                kw = cmd
            else:
                arg = cmd[2:]
                kw = cmd[:2]
            if kw == b"FA":
                out = self.process_FA(arg=arg, vfo=0)
                if not self.recv_freq[0]: out = None
            elif kw == b"FB":
                out = self.process_FA(arg=arg, vfo=1)
                if not self.recv_freq[1]: out = None
            else: out = None
            if out: self.sp.write(out)
        return

    def main(self):
        if not self.speclab.hwnd:
            sys.stderr.write("Failed to locate Spectrum Lab!")
            return
        try:
             while True:
                 time.sleep(0.001)
                 self.run_buffer()
                 self.process_commands()
        except KeyboardInterrupt:
             self.sp.close()

def main():
    if len(sys.argv) < 3:
        print("""speclab_sync.py com_port speclab_instance
com_port is the other end of the loopback from OmniRig (eg. COM12)
speclab_instance is the nth instance of Spectrum Lab you want to control
    (usually 1, for the first instance)""")
    else:
        if sys.argv[-1] == "v": verbose = True
        r = RigEmulator(port=sys.argv[1],
                        baudrate=BAUDRATE,
                        inst=int(sys.argv[2]),
                        verbose=verbose)
        r.main()

if __name__ == "__main__": main()

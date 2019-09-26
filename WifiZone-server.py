from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from time import sleep
import threading
import argparse
import socket
import os

class HTTPHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

class HTTPServer(BaseHTTPServer):
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

def server_thread_function(port, http_dir):
    try:
        global httpd
        httpd = HTTPServer(http_dir, ("", int(port)))
        httpd.serve_forever()
    except:
       print('port not available')
       messagebox.showinfo("Alert", "Port already in use try different")

def nsd_thread_function(service_name, path, port):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only
        
    desc = {'path': path}

    info = ServiceInfo(
        "_http._tcp.local.",
        service_name+"._http._tcp.local.",
        addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
        port=int(port),
        properties=desc,
        server="ash-2.local.",
    )
    #messagebox.showinfo("Alert", "In nsd Process")
    zeroconf = Zeroconf(ip_version=ip_version)
    while True:
        zeroconf.register_service(info)
        sleep(3)
        zeroconf.unregister_service(info)
        global stop_thread
        if(stop_thread):
            break

def select_folder():
    directory = filedialog.askdirectory()
    entry_select_folder.delete(0, END)
    entry_select_folder.insert(0, directory)
    print(directory)

def select_file():    
    if entry_select_folder.get() == "":
        messagebox.showinfo("Alert", "Select folder first")
        return
    file_path = filedialog.askopenfilename()
    file_path = file_path.replace(entry_select_folder.get()+'/', '')
    entry_select_file.delete(0, END)
    entry_select_file.insert(0, file_path)
    print(file_path)

def start_server():
    print('starting server.....')

    service_name = entry_service_name.get()
    path = entry_select_file.get()
    port = entry_port_number.get()
    http_dir = entry_select_folder.get()

    global server_thread, nsd_thread, stop_thread

    stop_thread = False

    server_thread = threading.Thread(target = server_thread_function, args = (port, http_dir, ))
    server_thread.start()
    
    nsd_thread = threading.Thread(target = nsd_thread_function, args = (service_name, path, port, ))
    nsd_thread.start()
    
    button_start['state'] = DISABLED
    button_stop['state'] = NORMAL 

def stop_server():
    
    global stop_thread, httpd, nsd_thread, server_thread
    
    stop_thread = True
    nsd_thread.join()
    print('service stopped !!')

    httpd.shutdown()
    server_thread.join()
    print('server stopped !!')

    button_start['state'] = NORMAL
    button_stop['state'] = DISABLED


if __name__ == "__main__":
    
    top = Tk()

    top.title('WifiZone Server')

    ip_address = socket.gethostbyname(socket.gethostname())

    label_service_name = Label(top, text="Service Name - ")
    label_service_name.grid(row = 0, column = 0, padx = (10,5), pady = (20,10))

    entry_service_name = Entry(top, bd = 2)
    entry_service_name.grid(row = 0, column = 1, pady = (20,10))

    label_ip_address = Label(top, text = "IP Address - ")
    label_ip_address.grid(row = 2, column = 0, padx = (10,5), pady = (5,10))

    label_ip_address = Label(top, text = ip_address)
    label_ip_address.grid(row = 2, column = 1, padx = (10,5), pady = (5,10))

    label_port_number = Label(top, text = "Port Number - ")
    label_port_number.grid(row = 3, column = 0, pady = (5,10))

    entry_port_number = Entry(top, bd = 2)
    entry_port_number.grid(row = 3, column = 1, pady = (5,10))

    entry_port_number.delete(0, END)
    entry_port_number.insert(0, "8000")

    label_select_folder = Label(top, text = "Select Folder - ")
    label_select_folder.grid(row = 4, column = 0, padx = (10,5), pady = (5,10))

    entry_select_folder = Entry(top, bd = 2)
    entry_select_folder.grid(row = 4, column = 1, pady = (5,10))

    button_select_folder = Button(top, text = "Browse", command = select_folder)
    button_select_folder.grid(row = 4, column = 2, padx=(5,5), pady = (5,10))

    label_select_file = Label(top, text = "Select Main File -")
    label_select_file.grid(row = 5, column = 0, padx = (10,5), pady = (5,10))

    entry_select_file = Entry(top, bd = 2)
    entry_select_file.grid(row = 5, column = 1, pady = (5,10))

    button_select_file = Button(top, text = "Browse", command = select_file)
    button_select_file.grid(row = 5, column = 2, padx=(5,5), pady = (5,10))

    label_space1 = Label(top, text="")
    label_space1.grid(row = 6, column = 0, padx = (10,5), pady = (5,10))

    button_start = Button(top, text = "Start", command = start_server)
    button_start.grid(row = 6, column = 1, padx=(20,10), pady = (20,10))

    button_stop = Button(top, text = "Stop", state = DISABLED,command = stop_server)
    button_stop.grid(row = 6, column = 2, padx=(20,10), pady = (20,10))

    top.mainloop()

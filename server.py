from threading import Thread    # multi threading/processing library
from database import database   # database class from database.py
import socket                   # network interface lib
import time                     # time lib
import subprocess               # command line execution lib
import struct                   # change native data to string of bytes lib
import cv2                      # camera, photo lib
import pickle                   # transfer complex data to byte stream with same structure
import os                       # operating system control lib
import numpy                    # array processing module

class server:
    IP_ADDRESS = ""                     #
    PORT = 9999                         #
    SERVER_RUNNING = False              # hidden variables/inbuild class variables
    IMAGES = [None,None,None,None]      #
    interval_set = False                #
    interval_sec = 0                    #
    def __init__(self):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # initialize socket module to create server class
        self.set_ip()                                                           # set ip address
                                                                                    
    def bind(self):                                                             
        self.socket.bind((server.IP_ADDRESS, server.PORT))                      # Create the server using socket module and set value
        server.SERVER_RUNNING = True                                            # True to SERVER_RUNNING variable and determine as a server flag
        self.socket.listen(5)                                                   #

    def set_ip(self):
        command_line_bytes = subprocess.Popen('ipconfig', stdin=subprocess.PIPE, stdout=subprocess.PIPE,# get command line output as 
                                              stderr=subprocess.PIPE).communicate()                     # bytes using "ipconfig"
        for bytes_row in command_line_bytes:                                                            #
            if bytes_row != b'':                                                                        #
                for string_row in bytes_row.decode('utf-8').split("\n"):                                # find/filter IPv4 private ip address where it
                    if string_row.strip().startswith("IPv4"):                                           # start from 192 and return value to function
                        if string_row.strip().split(":")[1].strip().startswith("192"):                  #
                            server.IP_ADDRESS = string_row.strip().split(":")[1].strip()                #
                            return
        server.IP_ADDRESS = socket.gethostname()                # if not found private IPv4 address in localmachine, return localhost string

    def accept_clients(self, threads):
        connected = False
        i = 0
        while True:                                                         #
            if server.SERVER_RUNNING:                                       #
                connected = True                                            #
                try:                                                        #
                    client, addr = self.socket.accept()                     # accept clients continuously to server with more clients
                    t = Thread(target=self.client_loop, args=(client,i))    # using while loop until the SERVER_RUNNING variable bool
                    t.start()                                               # is True
                    threads.append(t)                                       #
                    i += 1      # increase i value +1
                    if i > 3:   # check i value if less than 3
                        i = 0 # set i to 0
                except socket.error:                                        # 
                    server.SERVER_RUNNING = False                           # 
            else:                                                           # get error detail if occured and set server running flag
                if connected:                                               # to false
                    break                                                   #
                else:
                    pass
            time.sleep(0.5)                                                 # interval for this loop

    def client_loop(self, client, index):
        buff_size = 1024                    # buffer bytes size
        authendicated = False   # authendication flag
        bytes_data = b""                # string of bytes variable
        payload_size = struct.calcsize("Q") # get structure for "Q"
        client_username = ""    # username container
        interval_state = 0 
        while True:
            try:
                if server.SERVER_RUNNING:   # check if server running
                    if not authendicated:   # check if authendicated
                        client_msg = client.recv(buff_size).decode().split("/") # get data from clients
                        if client_msg[0] == "L":                                # check message contains "L"
                            if self.check_exists(client_msg[1], client_msg[2]):     #
                                client_username = client_msg[1]                     #
                                authendicated = True                                # client login process
                                client.send("success".encode())                     #
                            else:                                                   #
                                client.send("error1".encode())                      #
                        elif client_msg[0] == "S":                              # check message contains "S"
                            if self.insert(client_msg[1], client_msg[2]):           #
                                client.send("success".encode())                     #
                                client_username = client_msg[1]                     #
                                authendicated = True                                # insert clients/ sign up clients
                            else:                                                   #
                                client.send("error2".encode())                      #
                    elif authendicated:                     # check if authendicated
                        if interval_state == 0:         # check if interval is 0
                            if not Admin.interval_set:  # check if interval added current moment
                                client.send("s/5".encode()) # send interval time to client
                                interval_state = 1 # interval state to 1
                        elif Admin.interval_set:                                            #
                            if Admin.interval_sec < 1:                                      #
                                messagebox.showerror("Error", "second must more than 1sec") # send interval to client if 
                                continue                                                    # admin add new interval
                            client.send(f"s/{Admin.interval_sec}".encode())                 #
                            Admin.interval_set = False                                      #
                        try:
                            while len(bytes_data) < payload_size:                           #                   
                                packet = client.recv(4*buff_size)                           #
                                if not packet:                                              #
                                    break                                                   #
                                bytes_data += packet                                        # get image frames through sockets from 
                            packed_message_size = bytes_data[:payload_size]                 # employees and rearrange and resturture
                            bytes_data = bytes_data[payload_size:]                          # them.
                            message_size = struct.unpack("Q", packed_message_size)[0]       #
                            while len(bytes_data) < message_size:                           #
                                bytes_data += client.recv(4*buff_size)                      #
                            frame_bytes = bytes_data[:message_size]                         #
                            bytes_data = bytes_data[message_size:]                          #
                            frame = pickle.loads(frame_bytes)                               #
                            frame = cv2.resize(frame, (640, 480))   # resize image
                            self.insert_blob(client_username, client_username + str(time.asctime()), frame) # save frame to database
                            Admin.IMAGES[index] = frame # set image postion in IMAGES list with give index to client
                        except socket.error: # check server errors
                            Admin.IMAGES[index] = None  # if error occured set IMAGE list with given index to None
                else:
                    break # stop iteration
            except socket.error: # check for server errors
                Admin.IMAGES[index] = None  # if error occured set IMAGE list with given index to None
                break # stop iteration
            time.sleep(0.5) # loop delay
            
    def close(self):
        server.SERVER_RUNNING = False   # set SERVER_RUNNING variable from True into False
        self.socket.close()             # after disconnect the server

from tkinter import ttk
from tkinter import *               #
from tkinter import messagebox      # import gui library and windows kernel to find windows width and height dimentions
from PIL import ImageTk, Image
import ctypes                       #
import glob

class Admin(server, database):
    user32 = ctypes.windll.user32                                           #
    width = user32.GetSystemMetrics(0)                                      #
    height = user32.GetSystemMetrics(1)                                     #
    geometry = f"{int(width*0.5)}x{int(height*0.8)}+0+{int(height*0.05)}"   #
    threads = []                                                            # in build variable
    temp_files = []                                                         #
    labels = []                                                             #
    row = 0                                                                 #
    hide = True                                                             #
    pop_window = None                                                       #
    imshow = False                                                          #
    def __init__(self):
        server.__init__(self)       # initialize server class
        database.__init__(self)     # initialize own created from database.py database class
        self.master = Tk()          # initialize gui class
        self.master.geometry(Admin.geometry)    #
        self.master.title("ADMIN")              # set gui class properties
        self.master.resizable(False, False)     #
        # Login lable
        Label(self.master, text="LOGIN FORM", font=("sans-serif", 20, "bold"),
              fg="green").pack(side=TOP, pady=100)

        # String variables for gui
        self.username = StringVar()
        self.password = StringVar()
        self.interval = IntVar()

        # frames
        frm1 = Frame(self.master, width=300, height=50, bg="gray")
        frm1.pack(side=TOP, pady=10)
        frm2 = Frame(self.master, width=300, height=50, bg="gray")
        frm2.pack(side=TOP, pady=10)
        frm3 = Frame(self.master, width=300, height=50, bg="gray")
        frm3.pack(side=TOP, pady=10)

        # Entry for username
        lb = Label(frm1, text="username", font=("sans-serif", 12, "bold"), fg="white", bg="gray")
        lb.pack(side=LEFT, padx=10, pady=10)
        en1 = Entry(frm1, textvariable=self.username, font=("sans-serif", 12, "bold"), bg="white",
                    fg="gray", relief=SUNKEN, bd=2)
        en1.pack(side=LEFT, padx=10, pady=10)

        # Entry for password
        lb = Label(frm2, text="password", font=("sans-serif", 12, "bold"), fg="white", bg="gray")
        lb.pack(side=LEFT, padx=10, pady=10)
        en2 = Entry(frm2, textvariable=self.password, font=("sans-serif", 12, "bold"), bg="white",
                    fg="gray", relief=SUNKEN, bd=2)
        en2.pack(side=LEFT, padx=10, pady=10)

        # Buttons(Login, signup)
        bt1 = Button(frm3, text="Login", font=("sans-serif", 10, "bold"), bg="white", fg="gray",
                     command=self.login, width=15)
        bt1.pack(side=LEFT, padx=12, pady=10)
        bt2 = Button(frm3, text="Sign up", font=("sans-serif", 10, "bold"), bg="white", fg="gray",
                     command=self.signup, width=15)
        bt2.pack(side=LEFT, padx=12, pady=10)

        # Bindings for entries and buttons
        en1.bind("<Enter>", self.hover)
        en1.bind("<Leave>", self.unhover)
        en2.bind("<Enter>", self.hover)
        en2.bind("<Leave>", self.unhover)
        bt1.bind("<Enter>", self.hover)
        bt1.bind("<Leave>", self.unhover)
        bt2.bind("<Enter>", self.hover)
        bt2.bind("<Leave>", self.unhover)
        
        multi_task1 = Thread(target=self.accept_clients, args=(Admin.threads,)) #
        multi_task1.start()                                                     # start multi threading
        multi_task2 = Thread(target=self.show_live_update)                      #
        multi_task2.start()                                                     #
        
        self.master.mainloop()             # attach mainloop for gui class and show graphical window on desktop
        self.close()    # close server
        multi_task1.join()          #
        multi_task2.join()          # stop multi threaing 
        for t in Admin.threads:     # iterations
            t.join()                #

    def main(self):
        self.bind() # bind server
        # frame
        frm1 = Frame(self.master, width=100, height=100)
        frm1.pack(side=TOP, pady=20)
        # ip address panel(Label) 
        lb = Label(frm1, text=f"SERVER IP ADDRESS : {server.IP_ADDRESS}",
                   font=("sans-serif", 14, "bold"), fg="gray")
        lb.pack(side=LEFT, padx=20, pady=20)
        lb.bind("<Enter>", self.hover)
        lb.bind("<Leave>", self.unhover)

        # Tab
        tabs_panel = ttk.Notebook(self.master)
        # tab 1
        tab1 = ttk.Frame(tabs_panel)
        # Canvas
        lv_canvas = Canvas(tab1, width=640, height=500)
        lv_canvas.pack(side=LEFT, fill=BOTH, expand=1)
        ys1 = ttk.Scrollbar(tab1, orient=VERTICAL, command=lv_canvas.yview)
        ys1.pack(side=RIGHT, fill=Y)
        lv_canvas.configure(yscrollcommand=ys1.set)
        lv_canvas.bind('<Configure>', lambda e: lv_canvas.configure(scrollregion=lv_canvas.bbox('all')))
        self.img_container = Frame(lv_canvas)
        lv_canvas.create_window((0, 0), window=self.img_container, anchor=NW)
        # Frame
        mf1 = Frame(self.img_container, bg="gray")
        mf1.grid(row=0, column=0, padx=30, pady=30)
        Label(mf1, text="Interval(seconds)", font=("sans-serif", 12, "bold"), fg="white", bg="gray").grid(row=0, column=0, padx=10, pady=10)
        en = Entry(mf1, textvariable=self.interval, font=("sans-serif", 12, "bold"), fg="gray", bg="white", justify="right")
        en.grid(row=0, column=1, padx=10, pady=10)
        # Buttons and bindings
        btn = Button(mf1, text="set interval", command=self.set_interval, font=("sans-serif", 12, "bold"), bg="white", fg="gray")
        btn.grid(row=0, column=2, padx=10, pady=10)
        btn.bind("<Enter>", self.hover)
        btn.bind("<Leave>", self.unhover)
        en.bind("<Enter>", self.hover)
        en.bind("<Leave>", self.unhover)
        btn = Button(mf1, text="Show Current Update", command=self.show_or_hide_live, font=("sans-serif", 12, "bold"), bg="white", fg="gray")
        btn.grid(row=1, column=0, padx=10, pady=10)
        btn.bind("<Enter>", self.hover)
        btn.bind("<Leave>", self.unhover)
        # tab 2
        tab2 = ttk.Frame(tabs_panel)
        # Canvas
        lv_canvas2 = Canvas(tab2, width=640, height=500)
        lv_canvas2.pack(side=LEFT, fill=BOTH, expand=1)
        ys2 = ttk.Scrollbar(tab2, orient=VERTICAL, command=lv_canvas2.yview)
        ys2.pack(side=RIGHT, fill=Y)
        lv_canvas2.configure(yscrollcommand=ys2.set)
        lv_canvas2.bind('<Configure>', lambda e: lv_canvas2.configure(scrollregion=lv_canvas2.bbox('all')))
        self.img_container2 = Frame(lv_canvas2)
        lv_canvas2.create_window((0, 0), window=self.img_container2, anchor=NW)
        btn_row = 0
        for username in self.get_usernames():                                                   #
            if username[0] == "server":                                                         #
                continue                                                                        #
            lb = Label(self.img_container2, text=username[0], font=("sans-serif", 14, "bold"),  #
                       fg="gray", width=53)                                                     # 
            lb.grid(row=btn_row, column=0, padx=0, pady=0)                                      # show client list from database
            lb.bind("<Enter>", self.hover)                                                      #
            lb.bind("<Leave>", self.unhover)                                                    #
            lb.bind("<ButtonPress>", self.press_emp)                                            #
            btn_row += 1                                                                        #
            Admin.labels.append(username[0])                                                    #
        Admin.row = btn_row     
        tabs_panel.add(tab1, text="Live Employee Update")
        tabs_panel.add(tab2, text="Older Employee IMG")
        tabs_panel.pack(side=TOP, expand=YES)

    # set interval
    def set_interval(self):
        Admin.interval_set = True
        Admin.interval_sec = self.interval.get()

    # show or hide live image frame
    def show_or_hide_live(self):
        if Admin.hide:
            Admin.hide = False
        elif not Admin.hide:
            Admin.hide = True

    # show live update from clients in interval given by admin
    def show_live_update(self):
        connected = False
        while True:
            if server.SERVER_RUNNING:
                connected = True
                if not Admin.hide:
                    horizontal_1 = []
                    horizontal_2 = []
                    for i in range(len(server.IMAGES)):                         #
                        if i+1 <= 2:                                            #
                            if not(server.IMAGES[i] is None):                   #
                                horizontal_1.append(server.IMAGES[i])           #
                        elif i+1 >= 3:                                          #
                            if not(server.IMAGES[i] is None):                   #
                                horizontal_2.append(server.IMAGES[i])           #
                    novid = cv2.imread('error_cam.jpg')                         #
                    novid = cv2.resize(novid, (640, 480))                       # set image in horizontal order and vertical order
                    if len(horizontal_1) < 2:                                   #
                        for i in range(2-len(horizontal_1)):                    #
                            horizontal_1.append(novid)                          #
                        if len(horizontal_2) < 2:                               #
                            for i in range(2 - len(horizontal_2)):              #
                                horizontal_2.append(novid)                      #
                    elif len(horizontal_2) < 2:                                 #
                        for i in range(2-len(horizontal_2)):                    #
                            horizontal_2.append(novid)                          #
                    hor1 = numpy.concatenate([img for img in horizontal_1], axis=1)         # concatenate images
                    hor2 = numpy.concatenate([img for img in horizontal_2], axis=1)         #
                    hor1 = cv2.resize(hor1, (Admin.width-100, int((Admin.height-140)*0.5)))     # resize images
                    hor2 = cv2.resize(hor2, (Admin.width-100, int((Admin.height-140)*0.5)))     #
                    images = numpy.concatenate([hor1, hor2], axis=0) # concatenate all images
                    images = cv2.resize(images, (Admin.width-100, Admin.height-140)) # resize main image
                    cv2.imshow("ACTING EMPLOYEES", images) # show main image
                    if cv2.waitKey(1) & 0xFF == ord('q'): # check if 'q' or 'Q' press
                        Admin.hide = True # set hide state to true
                else:
                    cv2.destroyAllWindows() # destroy the window
            else:
                if connected:   #
                    break       # stop iteration
                else:           #
                    pass        #
            time.sleep(0.2) # loop delay

    # when press on employee label
    def press_emp(self, event):
        # destroy pop up window
        def destroy_pop():
            for file in glob.glob("all_temp/*.jpg"):
                os.remove(file)
            Admin.pop_window.destroy()
            Admin.pop_window = None
        if Admin.pop_window == None:
            # create pop up window
            Admin.pop_window = Tk()
            Admin.pop_window.geometry("700x500+100+40")
            Admin.pop_window.title(event.widget['text'])
            Admin.pop_window.protocol("WM_DELETE_WINDOW", destroy_pop)
            canvas = Canvas(Admin.pop_window)
            canvas.pack(side=LEFT, fill=BOTH, expand=1)
            scroll = ttk.Scrollbar(Admin.pop_window, orient=VERTICAL, command=canvas.yview)
            scroll.pack(side=RIGHT, fill=Y)
            canvas.configure(yscrollcommand=scroll.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            frm = Frame(canvas)
            canvas.create_window((0,0), window=frm, anchor=NW)
            imgs = self.get_all_blob(event.widget['text'])
            # write all image from selected client to all_temp folder
            for img in imgs:
                f = open(f"all_temp/{img[0].replace(':','-')}.jpg", 'wb')
                f.write(img[1])
                f.close()
            row = 0
            # get all image data from all_temp folder
            for img, r in zip(imgs, range(len(imgs))):
                lb = Label(frm, text=img[0], fg="gray", font=("sans-serif", 12, "bold"))
                lb.grid(row=r, column=0)
                lb.bind("<ButtonPress>", self.press_img)
                lb.bind("<Enter>", self.hover)
                lb.bind("<Leave>", self.unhover)
                row += 1
            Admin.pop_window.mainloop()
        elif Admin.pop_window:
            # delete all image from all_temp folder
            for file in glob.glob("all_temp/*.jpg"):
                os.remove(file)
            Admin.pop_window.destroy()
            Admin.pop_window = None

    # when press image label, show image in tkinter
    def press_img(self, event):
        Admin.imshow=True
        filename = "all_temp/"+event.widget['text']+".jpg"
        img = cv2.imread(filename.replace(':','-'))
        img = cv2.resize(img, (1280, 480))
        cv2.imshow(f"{filename}", img)
        cv2.waitKey(0)
        Admin.imshow=False

    # when login button press
    def login(self):
        if self.username.get() == "" or self.password.get() == "":
            messagebox.showerror("Error", "Entry feilds are required")
        else:
            if self.check_exists(self.username.get(), self.password.get()):
                self.username.set("")
                self.password.set("")
                self.clear_master_widgets()
                self.main()
            else:
                messagebox.showerror("Error", "username or password does not exits")

    # when sign button press
    def signup(self):
        if self.username.get() == "" or self.password.get() == "":
            messagebox.showerror("Error", "Entry feilds are required")
        else:
            if self.insert(self.username.get(), self.password.get()):
                self.username.set("")
                self.password.set("")
            else:
                messagebox.showerror("Error", "you are entred account is already exists")

    # when mouse cursor walk through a widget configure
    def hover(self, event):
        event.widget.config(bg="green", fg="white")

    # when mouse cursor walk through a widget configure
    def unhover(self, event):
        event.widget.config(bg="white", fg="gray")

    # delete all widget from main window
    def clear_master_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
Admin()

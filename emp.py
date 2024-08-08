from threading import Thread    
from tkinter import *
from tkinter import messagebox
import socket
import time
import ctypes
import pyautogui # automated gui to get screen shots
import cv2
import numpy
import struct
import pickle

# Camera class
class Capture:
    def __init__(self):
        self.video_cap = cv2.VideoCapture(0) # get camera object

    def get_frame_fcamera(self):
        return self.video_cap.read() # read images from camera object

    def get_screenshot_desktop(self):
        return pyautogui.screenshot()# get desktop screenshot

    def close_fcamera(self):
        self.video_cap.release()     # close video object

class Employee:
    # In build variables
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    geometry = f"{int(width * 0.5)}x{int(height * 0.8)}+{int(width * 0.48)}+{int(height * 0.05)}"
    CONNECTED_TO_SERVER = False
    USERNAME = ""
    INTERVAL = 0
    seconds = 0
    LOGIN = False
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket object
        self.socket.connect(("192.168.1.101", 9999))    # connect to target server using ip
        Employee.CONNECTED_TO_SERVER = True # set conntected flag to True
        # main window
        self.master = Tk()   
        self.master.geometry(Employee.geometry)
        self.master.resizable(False, False)
        self.master.title("Employee")
        # Login Lable
        Label(self.master, text="LOGIN FORM", font=("sans-serif", 20, "bold"),
              fg="green").pack(side=TOP, pady=100)
        # gui variables
        self.username = StringVar()
        self.password = StringVar()
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
        # Buttons for login and signup
        bt1 = Button(frm3, text="Login", font=("sans-serif", 10, "bold"), bg="white", fg="gray",
                     command=self.login, width=15)
        bt1.pack(side=LEFT, padx=12, pady=10)
        bt2 = Button(frm3, text="Sign up", font=("sans-serif", 10, "bold"), bg="white", fg="gray",
                     command=self.signup, width=15)
        bt2.pack(side=LEFT, padx=12, pady=10)
        # Bindings for Buttons and entries
        en1.bind("<Enter>", self.hover)
        en1.bind("<Leave>", self.unhover)
        en2.bind("<Enter>", self.hover)
        en2.bind("<Leave>", self.unhover)
        bt1.bind("<Enter>", self.hover)
        bt1.bind("<Leave>", self.unhover)
        bt2.bind("<Enter>", self.hover)
        bt2.bind("<Leave>", self.unhover)
        # start multi tasking
        multi_tasking1 = Thread(target=self.continue_recv)
        multi_tasking1.start()
        multi_tasking2 = Thread(target=self.continue_send_footage)
        multi_tasking2.start()
        
        self.master.mainloop() # mainloop for main window
        Employee.CONNECTED_TO_SERVER = False # set connection flag to False
        self.socket.close() # close server
        multi_tasking1.join()   # close threading iteration
        multi_tasking2.join()   #

    # dummi function
    def main_frame_work(self, username):
        pass

    # continuously recive data from server
    def continue_recv(self):
        buff_size = 1024 # buffer size
        while True:
            if Employee.CONNECTED_TO_SERVER: # check if connected to server
                try:
                    mfs = self.socket.recv(buff_size).decode() # get data from server
                    if mfs == "success":                                                            #
                        Employee.LOGIN = True                                                       #
                        self.main_frame_work(Employee.USERNAME)                                     #
                    elif mfs == "error1":                                                           #
                        messagebox.showerror("Error", "username or password does not exits")        # get details from server control
                    elif mfs == "error2":                                                           # employee camera and interval time
                        messagebox.showerror("Error", "you are entered account already exists")     #
                    elif mfs.split("/")[0] == "s":                                                  #
                        Employee.INTERVAL = int(mfs.split("/")[1])                                  #
                        Employee.seconds = 0                                                        #
                except socket.error:
                    break # if error ocurred stop iteration
            else:
                break
            time.sleep(0.5) # loop delay

    # send images in given interval 
    def continue_send_footage(self):
        initiated = False
        capture = Capture()# get camera object 
        while True:
            if Employee.CONNECTED_TO_SERVER and Employee.LOGIN:  # check server running and if login
                initiated = True
                if Employee.seconds == Employee.INTERVAL:
                    try:
                        ret, frame = capture.get_frame_fcamera()                            #
                        desktop_frame = capture.get_screenshot_desktop()                    #
                        frame = cv2.resize(frame, (640, 480))                               # get camera capture and desktop 
                        desktop_frame = cv2.resize(numpy.array(desktop_frame), (640, 480))  # screen shots, after resize frames
                        frame = numpy.concatenate([frame, desktop_frame], axis=1)           # and converto string of bytes and 
                        frame = pickle.dumps(frame)                                         # restucture. after send all data to server
                        packet = struct.pack("Q", len(frame)) + frame                       #   
                        self.socket.sendall(packet)                                         #
                        Employee.seconds = 0                                                #
                    except socket.error:
                        capture.close_fcamera() # close camera object
                        break
                Employee.seconds += 1
            else:                               #
                if initiated:                   #
                    capture.close_fcamera()     # break iteration
                    break                       #
                else:                           #
                    pass                        #
            time.sleep(1)

    # login when press login button
    def login(self):
        if self.username.get() == "" or self.password.get() == "":
            messagebox.showerror("Error", "Entry feilds are required")
        else:
            self.socket.send(f"L/{self.username.get()}/{self.password.get()}".encode())
            Employee.USERNAME = self.username.get()
            self.username.set("")
            self.password.set("")

    # signup when press signup button
    def signup(self):
        if self.username.get() == "" or self.password.get() == "":
            messagebox.showerror("Error", "Entry feilds are required")
        else:
            self.socket.send(f"S/{self.username.get()}/{self.password.get()}".encode())
            Employee.USERNAME = self.username.get()
            self.username.set("")
            self.password.set("")

    # hover events 
    def hover(self, event):
        event.widget.config(bg="green", fg="white")

    def unhover(self, event):
        event.widget.config(bg="white", fg="gray")

    def clear_master_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

Employee()

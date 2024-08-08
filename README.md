# Remote Employee Monitoring System

This is a hypothetical Remote Employee Monitoring System developed using Python. The project consists of two parts: the HR side and the employee side. Every minute, the system sends snapshots from employees' cameras and desktops to the HR dashboard, allowing HR to monitor employee activity and ensure productivity.

## Implementation Steps

### Step 1: Install External Python Modules

Click the `"double click to install all extenal modules.py"` file to download and install the required external Python modules.

### Step 3: Configure and Open the Employee-Side Application

- Configure the server (HR PC's IP address) in the emp file by modifying the following line:
    ("self.socket.connect(("192.168.1.101", 9999))    # connect to target server using IP")
- Open the `"emp"` file on the employee's computer.
- Place the `"startup"` file in the following directory: `C:\Windows\System32`.
- This ensures that the login page automatically pops up when the employee turns on the computer.

### Step 4: Set Up the HR Dashboard

- Open the `"server"` file to launch the HR dashboard, which will allow HR to monitor employee activity in real-time.



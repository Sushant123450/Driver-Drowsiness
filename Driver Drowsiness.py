import cv2
import pygame
import dlib
from scipy.spatial import distance
from imutils import face_utils, resize
import time
import tkinter as Tk
from tkinter import ttk
import mysql.connector as Sql_con
from tkinter import messagebox

# Comment this part to remove MySQL Dependency
Database = Sql_con.connect(host="localhost", user="root", password="Sushant")
Cursor = Database.cursor()
Cursor.execute("Create Database if not exists Drivers")
Cursor.execute('use Drivers')
Cursor.execute("""CREATE TABLE IF NOT EXISTS Driver (
               DriverID INT Unique NOT nULL,
               Driver_Name varchar(25) Not Null,
               Threshold FLOAT(8,6) NOT NULL);
               """)
Database.commit()
# Till here 

flag = 0
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

detect = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "shape_predictor_68_face_landmarks.dat")


def ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    Eye_ear = (A+B)/(2.0 * C)
    return Eye_ear


def Calibration():
    baseline_data = []
    capture_duration = 10

    capture = cv2.VideoCapture(0)
    start_time = time.time()

    Sum_of_Baseline_data = 0
    Number_of_Baseline_data = 0

    Desired_Frame_rate = 60
    frame_interval = 1.0/Desired_Frame_rate

    while time.time() - start_time < capture_duration:
        ret, frame = capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detect(gray, 0)

        for subject in subjects:
            shape = predictor(gray, subject)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = ear(leftEye)
            rightEAR = ear(rightEye)
            Avg_ear = (leftEAR + rightEAR) / 2.0
            Sum_of_Baseline_data += Avg_ear
            Number_of_Baseline_data += 1

    
    baseline_EAR = Sum_of_Baseline_data / Number_of_Baseline_data
    initial_threshold = baseline_EAR * 0.8
    Thresh.insert(0, initial_threshold)


def Save():
    if DriverID.get()!="":

        Cursor.execute(
            "SELECT DriverID FROM driver WHERE DriverID = %s", (DriverID.get(),))
        result = Cursor.fetchone()
        if result is None:
            Input = (DriverID.get(), Driver_Name.get(), Thresh.get())
            if Input[1] != "" and Input[2] != "":
                Save_Query = "Insert into Driver(DriverID,Driver_Name,Threshold) Values (%s,%s,%s)"
                Cursor.execute(Save_Query, Input)
                Database.commit()
            else:
                Tk.messagebox.showwarning(
                    "Warning", "The Driver Name or Threshold Value for new Driver can not be empty")
        else:
            if Driver_Name.get() == "":
                Cursor.execute(
                    "SELECT Driver_Name FROM driver WHERE DriverID = %s", (DriverID.get(),))
                result = Cursor.fetchone()
                Input = (result[0], Thresh.get(), DriverID.get())
            else:
                Input = (Driver_Name.get(), Thresh.get(), DriverID.get())
            Update_query = "Update driver SET Driver_Name= %s, Threshold= %s WHERE DriverID=%s"
            Cursor.execute(Update_query, Input)
            Database.commit()
            Tk.messagebox.showinfo("Update Status", "The values are updated")
        DriverID.delete(0, Tk.END)
        Driver_Name.delete(0, Tk.END)
        Thresh.delete(0, Tk.END)
            
    else:
        Tk.messagebox.showwarning(
                    "Warning", "The Driver ID can not be empty")


def Show():
    
    Show_Window = Tk.Tk()
    Show_Window.title("Records")
    Show_Window.minsize(300, 200)
    Show_Window.configure(bg="#e0ffff")

    
    Tk.Label(Show_Window, text="DriverID", bg="#e0ffff", font=(
        "Helvetica", 12, "bold")).grid(row=0, column=0)
    Tk.Label(Show_Window, text="Driver Name", bg="#e0ffff",
             font=("Helvetica", 12, "bold")).grid(row=0, column=1)
    Tk.Label(Show_Window, text="Threshold", bg="#e0ffff",
             font=("Helvetica", 12, "bold")).grid(row=0, column=2)
    
    if DriverID.get()=="" and Driver_Name.get()=="":
        Show_Query = "Select * from Driver"
        Cursor.execute(Show_Query)
    elif DriverID.get()!="":
        Show_Query = 'Select * from Driver where DriverID=%s'
        Cursor.execute(Show_Query,(DriverID.get(),))
    elif Driver_Name.get()!="":
        Show_Query = "Select * from Driver where Driver_Name=%s"
        Cursor.execute(Show_Query,(Driver_Name.get(),))
    Result=Cursor.fetchall()
    row_num = 1
    for records in Result:
        Tk.Label(Show_Window, text=records[0], bg="#e0ffff").grid(
            row=row_num, column=0)
        Tk.Label(Show_Window, text=records[1], bg="#e0ffff").grid(
            row=row_num, column=1)
        Tk.Label(Show_Window, text=records[2], bg="#e0ffff").grid(
            row=row_num, column=2)
        row_num += 1
    Tk.Button(Show_Window,text="Close",command=Show_Window.destroy).grid(row=row_num+1, column=3)
    Show_Window.mainloop()


def Delete():
    if DriverID.get()!="":
        Delete_Query="Delete from Driver where DriverID=%s"
        Input=(DriverID.get(),)
        Cursor.execute(Delete_Query,Input)
        Database.commit()
        Tk.messagebox.showinfo("Delete Status", "The values are deleted")
        DriverID.delete(0, Tk.END)
        Driver_Name.delete(0, Tk.END)
        Thresh.delete(0, Tk.END)
    else:
        Tk.messagebox.showinfo('Delete Error','Please enter the driver id')


def Start_program():
    if DriverID.get()=="" and Thresh.get()=="":
        thresh = 0.20
    elif DriverID.get()=="" and Thresh.get()!="":
        thresh=float(Thresh.get())
    else:
        Fetch_query="Select Threshold from Driver WHERE DriverID=%s"
        Input=(DriverID.get(),)
        Cursor.execute(Fetch_query,Input)
        Result=Cursor.fetchone()
        thresh=float(Result[0])
        print(thresh)

    frame_check = 30
    flag = int(0)
    Desired_Frame_rate = 60
    frame_interval = 1.0/Desired_Frame_rate
    pygame.mixer.init()
    Alert = pygame.mixer.Sound("beep-06.wav")

    Video = cv2.VideoCapture(0)
    start_time = time.time()
    previous_frame_time = start_time

    while True:
        ret, frame = Video.read(0)
        frame = resize(frame, height=400, width=600)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detect(gray, 0)
        for subject in subjects:
            shape = predictor(gray, subject)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = ear(leftEye)
            rightEAR = ear(rightEye)
            Avg_ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
            if Avg_ear <= thresh:
                flag += 1
                print(flag)
                if (flag >= frame_check):
                    print("Alert")
                    Alert.play()
                    cv2.putText(frame, "SLEEP ALERT", (40, 20),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            else:
                Alert.stop()
                flag = 0

        current_time = time.time()
        frame_processing_time = current_time - previous_frame_time
        time_remaining = max(0, frame_interval - frame_processing_time)
        time.sleep(time_remaining)
        previous_frame_time = current_time

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    Video.release()
    cv2.destroyAllWindows()


def Exit_program():
    root.quit()


root = Tk.Tk()
root.configure(bg="#e0ffff")
root.minsize(400, 300)
root.title("Drowsiness Detection")

Tk.Button(root, text="Start", command=Start_program).grid(row=5, column=0)
Tk.Button(root, text="Auto Calibrate",command=Calibration).grid(row=5, column=1)
Tk.Button(root, text="Exit", command=Exit_program).grid(row=5, column=2)

Tk.Label(root, text="Driver ID", bg="#e0ffff").grid(row=0, column=0)
DriverID = Tk.Entry(root)
DriverID.grid(row=0, column=1)

Tk.Label(root, text="Driver Name", bg="#e0ffff").grid(row=1, column=0)
Driver_Name = Tk.Entry(root)
Driver_Name.grid(row=1, column=1)

Tk.Label(root, text="Threshold", bg='#e0ffff').grid(row=2, column=0)
Thresh = Tk.Entry(root)
Thresh.grid(row=2, column=1)

Tk.Button(root, text="Save", command=Save).grid(row=3, column=0)
Tk.Button(root, text="Show", command=Show).grid(row=3, column=1)
Tk.Button(root, text="Delete", command=Delete).grid(row=3, column=2)

Instruction1=Tk.Label(root, text=''' Default Threshold Value= 0.20''',bg='#e0ffff')
Instruction2=Tk.Label(root, text=''' Use blank Space for default value''',bg='#e0ffff')
Instruction3=Tk.Label(root, text=''' Enter Driver ID to use already stored value''',bg='#e0ffff')
Instruction4=Tk.Label(root, text=''' Enter custom value in Threshold''',bg='#e0ffff')

Instruction1.place(x=10,y=150)
Instruction2.place(x=10,y=170)
Instruction3.place(x=10,y=190)
Instruction4.place(x=10,y=210)
root.mainloop()
import datetime, chime
from PyQt6.QtWidgets import *
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt
from showSchedule import ShowSchedule, ShowActivitySchedule, showHomePage
from showAppointments import ShowAllAppointments,ShowAppointments
from updateAppointments import insertOneTimeAppointment, insertReccuringAppointment, removeOneTimeAppointment, removeReccuringAppointment
from updateSchedule import insertSchedule, removeSchedule
from showAppointments import *
from wheather import Weather
import sqlite3


#Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
#Set up the UI
    def initUI(self):
        self.setWindowTitle("Virtual Assistant")
        self.setGeometry(200, 100, 1000, 550)

        self.label1 = QLabel(self)
        self.label1.move(30, 500)
        self.label1.resize(480, 30)

        self.lblclock = QLabel(self)
        self.lblclock.move(50, 450)
        self.lblclock.resize(400, 25)
        self.lblclock.setFont(QFont("Arial",24))
        
        self.textbox = QLineEdit(self)
        self.textbox.move(575, 450)
        self.textbox.resize(400, 30)

        self.button = QPushButton('Send', self)
        self.button.move(450, 450)
        self.button.clicked.connect(self.onClick)
       
        self.label_logo = QLabel(self)
        pixmap = QPixmap('logo.png')
        self.label_logo.setPixmap(pixmap)
        self.label_logo.resize(520, 400)
        self.label_logo.move(30, 30)

        self.chat_area = QTextEdit(self)
        self.chat_area.setGeometry(575, 30, 400, 400)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("border: 1px solid #3DED97;")

        #table schedule/appointments
        self.view = QTableWidget(self)
        self.view.move(30, 30)
        self.view.resize(520, 400)
        self.view.setVisible(False)
        
        # creating a timer object
        timer = QTimer(self)
        self.timer_weather = QTimer(self)
        # adding action to timer
        timer.timeout.connect(self.showTime)
        self.timer_weather.timeout.connect(self.weatherInfo)
        #execute weather function every 1h
        self.timer_weather.start(3600000)
        # update the timer every second
        timer.start(1000)
        
        self.show()

    #make a beep
    def succSound(self):
        chime.theme('big-sur')
        chime.info()

    def errSound(self):
        chime.theme('pokemon')
        chime.error()

    def tableUI(self):
        self.view.setVisible(True)
        self.label_logo.setVisible(False)

    def weatherInfo(self):
        weather_data = Weather.checkCurrentWeather()
        self.assistantResponse(weather_data)
        if "rain" in weather_data:
           self.assistantResponse("It's raining! Don't forget your umbrella.")
        self.update()
    
    # method called by timer
    def showTime(self):
        # getting current time
        current_time = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # converting QTime object to string
        
        # showing it to the label
        self.lblclock.setText(str(current_time))
    
    def homePage(self):
        self.view.setVisible(False)
        self.label_logo.setVisible(True)

    def onClick(self):
        command = self.textbox.text()
        self.textbox.setText("")

        user_input = command.strip()
        ctime = datetime.datetime.today().strftime("%H:%M:%S")
        self.chat_area.append(f"<p style='color:#333333;font-family: georgia'><b>Me:</b> {user_input} [{ctime}]</p>")
        
        strategies = [
            ShowSchedule(),
            ShowActivitySchedule(),
            ShowAllAppointments(),
            ShowAppointments(),
            insertSchedule(),
            removeSchedule(),
            insertOneTimeAppointment(),
            removeOneTimeAppointment(),
            insertReccuringAppointment(),
            removeReccuringAppointment(),
            showHomePage()
        ]
        #Search right strategy
        for strategy in strategies:
            strategy.execute(self,command)

    def dialogErorr(self,string):
        self.chat_area.append(f"<p style='color:#333333;font-family: georgia'><b>Sophia:</b> Error :> {string}</p>")
        self.errSound()
        
    def assistantResponse(self,string):
        ctime = datetime.datetime.today().strftime("%H:%M:%S")
        self.chat_area.append(f"<p style='color:#333333;font-family: georgia'><b>Sophia:</b> {string} [{ctime}]</p>")

    def showSchedule(self, sqlquery):
        try:
            self.view.setColumnCount(4)
            self.view.setHorizontalHeaderLabels(["Time Start", "Time Stop", "Activity", "Location"])
            
            sqlCount = "SELECT COUNT(*) FROM "+sqlquery[13:]

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur2 = con.cursor()

            cur2.execute(sqlCount)
            r = cur2.fetchone()
            
            self.view.setRowCount(int(r[0]))
            tableRow = 0
            cur.execute(sqlquery)

            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(row[3]))
                self.view.setItem(tableRow, 3, QTableWidgetItem(row[4]))

                tableRow += 1
        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()

    def showOneTimeAppointments(self, sqlquery):
        try:
            self.view.setColumnCount(6)
            self.view.setHorizontalHeaderLabels(["Date", "Time Start", "Time Stop", "Activity", "Location"])
            sqlCount = "SELECT COUNT(*) FROM AppointmentsOneTime"

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur2 = con.cursor()

            cur2.execute(sqlCount)
            r = cur2.fetchone()
            self.view.setRowCount(int(r[0]))
            tableRow = 0
            cur.execute(sqlquery)

            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(row[3]))
                self.view.setItem(tableRow, 3, QTableWidgetItem(row[4]))
                self.view.setItem(tableRow, 4, QTableWidgetItem(row[5]))

                tableRow += 1

        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()

    def showRecurringAppointments(self, sqlquery):
        try:
            self.view.setColumnCount(7)
            self.view.setHorizontalHeaderLabels(["Date Start", "Date Stop", "Time Start", "Time Stop", "Activity", "Location"])
            sqlCount = "SELECT COUNT(*) FROM AppointmentsReccuring"

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur2 = con.cursor()

            cur2.execute(sqlCount)
            r = cur2.fetchone()
            self.view.setRowCount(int(r[0]))
            tableRow = 0
            cur.execute(sqlquery)
            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(str(row[3])))
                self.view.setItem(tableRow, 3, QTableWidgetItem(str(row[4])))
                self.view.setItem(tableRow, 4, QTableWidgetItem(row[5]))
                self.view.setItem(tableRow, 5, QTableWidgetItem(row[6]))

                tableRow += 1
        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()

    def showAppointmentsDate(self,date):
        try:
            self.view.setColumnCount(6)
            self.view.setHorizontalHeaderLabels(["Date", "Time Start", "Time Stop", "Activity", "Location"])
            sql_count_one = "SELECT COUNT(*) FROM AppointmentsOneTime WHERE Date ='"+str(date)+"'"
            sql_count_rec = "SELECT COUNT(*) FROM AppointmentsReccuring WHERE DateStop >='"+str(date)+"' AND DateStart<='"+str(date)+"'"
            sql_query_one = "SELECT * FROM AppointmentsOneTime WHERE Date ='"+str(date)+"' ORDER BY TimeStart"
            sql_query_rec = "SELECT * FROM AppointmentsReccuring WHERE DateStop >='"+str(date)+"' AND DateStart<='"+str(date)+"' ORDER BY TimeStart"

            print(sql_query_rec)
            print(sql_query_one)
            print(sql_count_one)
            print(sql_count_rec)

            con = sqlite3.connect("database.db")
            curO = con.cursor()
            curR = con.cursor()
            curCO = con.cursor()
            curCR = con.cursor()

            curCO.execute(sql_count_one)
            curCR.execute(sql_count_rec)
            r1 = curCO.fetchone()
            r2 = curCR.fetchone()

            self.view.setRowCount(int(r1[0])+int(r2[0]))
            tableRow = 0

            curO.execute(sql_query_one)
            curR.execute(sql_query_rec)

            for row in curO.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(row[3]))
                self.view.setItem(tableRow, 3, QTableWidgetItem(row[4]))
                self.view.setItem(tableRow, 4, QTableWidgetItem(row[5]))

                tableRow += 1

            for row in curR.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(date)))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[3])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(row[4]))
                self.view.setItem(tableRow, 3, QTableWidgetItem(row[5]))
                self.view.setItem(tableRow, 4, QTableWidgetItem(row[6]))

                tableRow += 1

        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()

    def ShowActivities(self,sqlquery):
        try:
            self.view.setColumnCount(5)
            self.view.setHorizontalHeaderLabels(["Day","Time Start", "Time Stop", "Activity", "Location",])

            con = sqlite3.connect("database.db")
            cur = con.cursor()

            self.view.setRowCount(10)
            tableRow = 0
            cur.execute(sqlquery)

            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[5])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 3, QTableWidgetItem(row[3]))
                self.view.setItem(tableRow, 4, QTableWidgetItem(row[4]))

                tableRow += 1
        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()

            
        
        

        

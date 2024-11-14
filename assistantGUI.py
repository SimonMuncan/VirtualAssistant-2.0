import datetime, chime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import *
from RainbowBar import RainbowBar
from showSchedule import ShowSchedule, ShowActivitySchedule, showHomePage
from showAppointments import ShowAllAppointments,ShowAppointments
from showWeather import ShowWeatherPage
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
        self.setWindowTitle("Sophia - Virtual Assistant")
        self.setGeometry(200, 100, 1000, 550)
        self.setWindowIcon(QIcon("pictures/icon.jpg"))
        # self.setMaximumSize(1000,530)

        self.lblclock = QLabel(self)
        self.lblclock.move(775, 500)
        self.lblclock.resize(400, 25)
        self.lblclock.setFont(QFont("Arial",16))
        
        self.textbox = QLineEdit(self)
        self.textbox.move(575, 450)
        self.textbox.resize(400, 30)

        self.button = QPushButton('Send', self)
        self.button.move(450, 450)
        self.button.clicked.connect(self.onClick)
       
        self.label_logo = QLabel(self)
        pixmap = QPixmap("pictures/logo.png")
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

        self.view.cellChanged.connect(self.updateDatabaseSchedule)
        self.view.cellChanged.connect(self.updateDatabaseOneTime)
        self.view.cellChanged.connect(self.updateDatabaseReccuring)

        
        self.timer_schedule = QTimer(self)
        self.timer_schedule.timeout.connect(self.checkSchedule)
        self.timer_schedule.start(60000)
        #initialize weather page
        self.weatherGUI()

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
        self.groupBoxWeather.setVisible(False)


        self.schedule_flag = False
        self.onetime_flag = False
        self.reccuring_flag = False

    def homePage(self):
        self.view.setVisible(False)
        self.label_logo.setVisible(True)
        self.groupBoxWeather.setVisible(False)


        self.schedule_flag = False
        self.onetime_flag = False
        self.reccuring_flag = False

    def weatherPage(self):
        self.view.setVisible(False)
        self.label_logo.setVisible(False)
        self.groupBoxWeather.setVisible(True)

        self.onetime_flag = False
        self.schedule_flag = False
        self.reccuring_flag = False
    
    #GUI for the weather page
    def weatherGUI(self):
        self.groupBoxWeather = QGroupBox(self)
        self.groupBoxWeather.setGeometry(30,30, 520, 400)  # Set position and size of the group box
        response_current = Weather.checkCurrentWeather()
        response_forecast = Weather.forecast3days()
        
        # Create the weather label
        self.lblWeather = QLabel(self.groupBoxWeather)
        self.lblWeather.setGeometry(20, 2, 400, 25)  # Set position and size of the label
        self.lblWeather.setFont(QFont("Arial", 12))
        self.lblWeather.setText(f"Current Weather in {response_current['location']['name']}")
        #if UV is high inform user
        self.getUV(response_current['current']['uv'])
        #Lable of current temperature
        self.lblCurrentTemp = QLabel(self.groupBoxWeather)
        self.lblCurrentTemp.setGeometry(50, 70, 50, 50) 
        self.lblCurrentTemp.setFont(QFont("Arial", 12))
        self.lblCurrentTemp.setText(f"{str(response_current['current']['temp_c'])}°C")
        #Picture of current temp
        self.lblCurrentTempPic = QLabel(self.groupBoxWeather)
        weather_pic_path = self.returnWeatherPicture(response_current['current']['condition']['text'])
        pixmap2 = QPixmap(weather_pic_path)  
        self.lblCurrentTempPic.setPixmap(pixmap2)
        self.lblCurrentTempPic.resize(100, 100)
        self.lblCurrentTempPic.move(45, 10)
        #Current parameters
        self.lblCurrentParam = QLabel(self.groupBoxWeather)
        self.lblCurrentParam.setGeometry(150, -7, 180, 150) 
        self.lblCurrentParam.setFont(QFont("Arial", 11))
        self.lblCurrentParam.setText(f"Wind speed: {str(response_current['current']['wind_kph'])} km/h\nPreasure: {str(response_current['current']['pressure_mb'])} mbar\nHumidity: {str(response_current['current']['humidity'])} %\nUV: {str(response_current['current']['uv'])}")
        
        #Create the 3days forecast label
        self.lblWeather = QLabel(self.groupBoxWeather)
        self.lblWeather.setGeometry(20, 140, 400, 25)  # Set position and size of the label
        self.lblWeather.setFont(QFont("Arial", 12))
        self.lblWeather.setText(f"3 days forecast in {response_current['location']['name']}")
        #day one
        self.lbl1stDay = QLabel(self.groupBoxWeather)
        self.lbl1stDay.setGeometry(30, 130, 100, 100) 
        self.lbl1stDay.setFont(QFont("Arial", 12))
        self.lbl1stDay.setText(str(self.findDay(datetime.datetime.weekday(datetime.datetime.strptime(response_forecast['forecast']['forecastday'][0]['date'],'%Y-%m-%d')))))
        #Lable of 1st day temperature
        self.lbl1stTemp = QLabel(self.groupBoxWeather)
        self.lbl1stTemp.setGeometry(30, 225, 100, 100) 
        self.lbl1stTemp.setFont(QFont("Arial", 12))
        self.lbl1stTemp.setText(f"Max: {str(response_forecast['forecast']['forecastday'][0]['day']['maxtemp_c'])}°C\nMin: {str(response_forecast['forecast']['forecastday'][0]['day']['mintemp_c'])}°C\n")
        print(response_forecast['forecast']['forecastday'][0]['date'])
        #Picture of 1st day temp
        self.lbl1stTempPic = QLabel(self.groupBoxWeather)
        weather_pic_path_1 = self.returnWeatherPicture(response_forecast['forecast']['forecastday'][0]['day']['condition']['text'])
        pixmap1st = QPixmap(weather_pic_path_1)  
        self.lbl1stTempPic.setPixmap(pixmap1st)
        self.lbl1stTempPic.resize(100, 100)
        self.lbl1stTempPic.move(45, 170)
        #day two
        self.lbl2ndDay = QLabel(self.groupBoxWeather)
        self.lbl2ndDay.setGeometry(150, 130, 100, 100) 
        self.lbl2ndDay.setFont(QFont("Arial", 12))
        self.lbl2ndDay.setText(str(self.findDay(datetime.datetime.weekday(datetime.datetime.strptime(response_forecast['forecast']['forecastday'][1]['date'],'%Y-%m-%d')))))
        #Lable of 2nd day temperature
        self.lbl2ndTemp = QLabel(self.groupBoxWeather)
        self.lbl2ndTemp.setGeometry(150, 225, 100, 100) 
        self.lbl2ndTemp.setFont(QFont("Arial", 12))
        self.lbl2ndTemp.setText(f"Max: {str(response_forecast['forecast']['forecastday'][1]['day']['maxtemp_c'])}°C\nMin: {str(response_forecast['forecast']['forecastday'][0]['day']['mintemp_c'])}°C\n")
        print(response_forecast['forecast']['forecastday'][1]['date'])
        #Picture of 2nd day temp
        self.lbl2ndTempPic = QLabel(self.groupBoxWeather)
        weather_pic_path_2 = self.returnWeatherPicture(response_forecast['forecast']['forecastday'][1]['day']['condition']['text'])
        pixmap2nd = QPixmap(weather_pic_path_2)  
        self.lbl2ndTempPic.setPixmap(pixmap2nd)
        self.lbl2ndTempPic.resize(100, 100)
        self.lbl2ndTempPic.move(165, 170)
        #day three
        self.lbl3rdDay = QLabel(self.groupBoxWeather)
        self.lbl3rdDay.setGeometry(265, 130, 100, 100) 
        self.lbl3rdDay.setFont(QFont("Arial", 12))
        self.lbl3rdDay.setText(str(self.findDay(datetime.datetime.weekday(datetime.datetime.strptime(response_forecast['forecast']['forecastday'][2]['date'],'%Y-%m-%d')))))
        #Lable of 3rd day temperature
        self.lbl3rdTemp = QLabel(self.groupBoxWeather)
        self.lbl3rdTemp.setGeometry(265, 225, 100, 100) 
        self.lbl3rdTemp.setFont(QFont("Arial", 12))
        self.lbl3rdTemp.setText(f"Max: {str(response_forecast['forecast']['forecastday'][2]['day']['maxtemp_c'])}°C\nMin: {str(response_forecast['forecast']['forecastday'][0]['day']['mintemp_c'])}°C\n")
        print(response_forecast['forecast']['forecastday'][2]['date'])
        #Picture of 3rd day temp
        self.lbl3rdTempPic = QLabel(self.groupBoxWeather)
        weather_pic_path_3 = self.returnWeatherPicture(response_forecast['forecast']['forecastday'][2]['day']['condition']['text'])
        pixmap3rd = QPixmap(weather_pic_path_3)  
        self.lbl3rdTempPic.setPixmap(pixmap3rd)
        self.lbl3rdTempPic.resize(100, 100)
        self.lbl3rdTempPic.move(280, 170)
        
        #AQI bar
        self.rainbowBar = RainbowBar(self.groupBoxWeather)
        self.rainbowBar.setGeometry(460, 30, 53, 250)  # Set position and size of the rainbow bar
        self.rainbowBar.setRandomValue()

        self.lblAQIContent = QLabel(self.groupBoxWeather)
        self.lblAQIContent.setGeometry(390, -10, 200, 50) 
        self.lblAQIContent.setFont(QFont("Arial", 12))
        self.lblAQIContent.setText("Air Quality Index")

        self.lblAQI = QLabel(self.groupBoxWeather)
        height, width = Weather.airQualityHeightWidth()
        self.lblAQI.setGeometry(width, height, 200, 50) 
        self.lblAQI.setFont(QFont("Arial", 12))
        self.lblAQI.setText(Weather.airQualityString())


        #Alerts
        #response_alerts = Weather.weatherAlerts()
        simul = "Yellow"
        simul2 = "Although rather usual in this region, locally or potentially dangerous phenomena are expected. (such as local winds, summer thunderstorms, rising streams or high waves)"
        self.lblAlerts = QLabel(self.groupBoxWeather)
        self.lblAlerts.setGeometry(20, 295, 400, 25)  # Set position and size of the label
        self.lblAlerts.setFont(QFont("Arial", 12))
        self.lblAlerts.setText(f"Alerts for {response_current['location']['name']}")

        self.alerts_area = QTextEdit(self.groupBoxWeather)
        self.alerts_area.setGeometry(20, 325, 480, 70)
        self.alerts_area.setReadOnly(True)
        self.alerts_area.setStyleSheet("border: 1px solid #FFFFFF;")
        #self.alerts_area.append(f"<p style='color:#333333;font-family: arial; size:12'> Alert: {response_alerts['alerts']['data'][0]['headline']} </p>")
        #self.alerts_area.append(f"<p style='color:#333333;font-family: arial; size:12'> {response_alerts['alerts']['data'][0]['description']} </p>")

        self.alerts_area.append(f"<p style='color:#333333;font-family: arial'> Alert: {simul} </p>")
        self.alerts_area.append(f"<p style='color:#333333;font-family: arial'> {simul2} </p>")

        self.groupBoxWeather.setVisible(False)

    def findDay(self, dayNumber):
        days = {7:"Sunday", 1:"Monday", 2:"Tuesday", 3:"Wednesday", 4:"Thursday", 5:"Friday", 6:"Saturday"}

        return days[dayNumber+1]
    
    def getUV(self, uv_factor):
        if uv_factor > 5 and uv_factor <= 7:
            self.assistantResponse("UV is high. Dont go outside unless it's necessary!")
        elif uv_factor >= 8 and uv_factor < 11:
            self.assistantResponse("UV is very high! Do not go outside! Put suncream on!")
        
    def returnWeatherPicture(self,string):
        print(string)
        if "heavy rain" in string.lower() or "moderate rain" in string.lower() and not "thunder" in string.lower():
            return "weather_pictures/rain.png"
        elif "light rain" in string.lower():
            return "weather_pictures/light rain"
        elif "cloudy" in string.lower() and not "partly" in string.lower():
            return "weather_pictures/cloudy"
        elif "thunder" in string.lower():
            return "weather_pictures/thunder"
        elif "snow" in string.lower():
            return "weather_pictures/snow"
        elif "partly cloudy" in string.lower():
            return "weather_pictures/mostly sunny"
        elif "sunny" in string.lower():
            return "weather_pictures/sunny"
        elif "windy" in string.lower():
            return "weather_pictures/wind"
        elif "patchy rain" in string.lower():
            return "weather_pictures/rain maybe.png"

    def weatherInfo(self):
        weather_data = Weather.checkCurrentWeather()
        #self.assistantResponse(weather_data)
        if "rain" in weather_data:
           self.assistantResponse("It's raining! Don't forget your umbrella.")
        elif "sunny" in weather_data:   
            self.assistantResponse("It's sunny!")
        self.update()

    # method called by timer
    def showTime(self):
        # getting current time
        current_time = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # converting QTime object to string
        
        # showing it to the label
        self.lblclock.setText(str(current_time))
    
    def checkSchedule(self):
        list_schedule = self.getSchedule(self.findDay(datetime.datetime.weekday(datetime.datetime.today())))
        for i in list_schedule:
            if i[0]== datetime.datetime.now().strftime("%H:%M"):
                self.assistantResponse(f"It's time for {str(i[1])} at {str(i[2])}")

    def onClick(self):
        command = self.textbox.text()
        self.textbox.setText("")

        user_input = command.strip()
        ctime = datetime.datetime.today().strftime("%H:%M")
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
            showHomePage(),
            ShowWeatherPage()
        ]
        #Search right strategy
        for strategy in strategies:
            strategy.execute(self,command)

    def dialogErorr(self,string):
        self.chat_area.append(f"<p style='color:#333333;font-family: georgia'><b>Sophia:</b> Error :> {string}</p>")
        self.errSound()
        
    def assistantResponse(self,string):
        ctime = datetime.datetime.today().strftime("%H:%M")
        self.chat_area.append(f"<p style='color:#333333;font-family: georgia'><b>Sophia:</b> {string} [{ctime}]</p>")

    def getSchedule(self, today):
        try:
            self.view.setColumnCount(5)
            self.view.setHorizontalHeaderLabels(["ID","Time Start", "Time Stop", "Activity", "Location"])
            
            sql_query = f"SELECT TimeStart,Activity,Location FROM {today}"

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute(sql_query)
            list = []
            for row in cur.fetchall():
                list.append(row)
            return list
        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()
        
    def showSchedule(self, sqlquery):
        try:
            self.view.setColumnCount(5)
            self.view.setHorizontalHeaderLabels(["ID","Time Start", "Time Stop", "Activity", "Location"])
            
            sqlCount = "SELECT COUNT(*) FROM "+sqlquery[13:]

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur2 = con.cursor()

            self.schedule_flag = True
            self.onetime_flag = False
            self.reccuring_flag = False

            cur2.execute(sqlCount)
            r = cur2.fetchone()
            name = re.search("(Monday|Tuesday|Wednesday|Thrusday|Friday|Saturday|Sunday|work)",sqlquery,re.IGNORECASE)
            self.table_name = name[0]
            self.view.setRowCount(int(r[0]))
            tableRow = 0
            cur.execute(sqlquery)
           
            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[0])))
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
    #update tables for schedule
    def updateDatabaseSchedule(self, row, column):
        if not self.schedule_flag:
            return
        try:
            con = sqlite3.connect("database.db")
            cur = con.cursor()

            # Fetch the values from the table
            id_item = self.view.item(row, 0)
            time_start_item = self.view.item(row, 1)
            time_stop_item = self.view.item(row, 2)
            activity_item = self.view.item(row, 3)
            location_item = self.view.item(row, 4)

            id = id_item.text() if id_item else ''
            time_start = time_start_item.text() if time_start_item else ''
            time_stop = time_stop_item.text() if time_stop_item else ''
            activity = activity_item.text() if activity_item else ''
            location = location_item.text() if location_item else ''

            # Assume the first column is the primary key or unique identifier
            # Update the database with the new values
            update_query = f"""
            UPDATE {self.table_name}
            SET TimeStart = "{str(time_start)}", TimeStop = "{str(time_stop)}", Activity = "{str(activity)}", Location = "{str(location)}", Day ="{self.table_name}"
            WHERE id = {int(id)}
            """
            #print(update_query)
            cur.execute(update_query) 
            con.commit()
        except sqlite3.Error as error:
            print("Failed to update the database", error)
        finally:
            if con:
                con.close()

    def showOneTimeAppointments(self, sqlquery):
        try:
            self.view.setColumnCount(6)
            self.view.setHorizontalHeaderLabels(["ID","Date", "Time Start", "Time Stop", "Activity", "Location"])
            sqlCount = "SELECT COUNT(*) FROM AppointmentsOneTime"

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur2 = con.cursor()

            self.schedule_flag = False
            self.onetime_flag = True
            self.reccuring_flag = False

            cur2.execute(sqlCount)
            r = cur2.fetchone()
            self.view.setRowCount(int(r[0]))
            tableRow = 0
            cur.execute(sqlquery)

            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[0])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 3, QTableWidgetItem(row[3]))
                self.view.setItem(tableRow, 4, QTableWidgetItem(row[4]))
                self.view.setItem(tableRow, 5, QTableWidgetItem(row[5]))

                tableRow += 1

        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()

    #update tables for one time
    def updateDatabaseOneTime(self, row, column):
        if not self.onetime_flag:
            return
        try:
            con = sqlite3.connect("database.db")
            cur = con.cursor()

            # Fetch the values from the table
            id_item = self.view.item(row, 0)
            date_item = self.view.item(row, 1)
            time_start_item = self.view.item(row, 2)
            time_stop_item = self.view.item(row, 3)
            activity_item = self.view.item(row, 4)
            location_item = self.view.item(row, 5)
            

            id = id_item.text() if id_item else ''
            date = date_item.text() if date_item else ''
            time_start = time_start_item.text() if time_start_item else ''
            time_stop = time_stop_item.text() if time_stop_item else ''
            activity = activity_item.text() if activity_item else ''
            location = location_item.text() if location_item else ''

            # Assume the first column is the primary key or unique identifier
            # Update the database with the new values
            update_query = f"""
            UPDATE AppointmentsOneTime
            SET Date = "{str(date)}", TimeStart = "{str(time_start)}", TimeStop = "{str(time_stop)}", Activity = "{str(activity)}", Location = "{str(location)}"
            WHERE id = {int(id)}
            """
            #print(update_query)
            cur.execute(update_query) 
            con.commit()
        except sqlite3.Error as error:
            print("Failed to update the database", error)
        finally:
            if con:
                con.close()

    def showRecurringAppointments(self, sqlquery):
        try:
            self.view.setColumnCount(7)
            self.view.setHorizontalHeaderLabels(["ID","Date Start", "Date Stop", "Time Start", "Time Stop", "Activity", "Location"])
            sqlCount = "SELECT COUNT(*) FROM AppointmentsReccuring"

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur2 = con.cursor()

            self.schedule_flag = False
            self.onetime_flag = False
            self.reccuring_flag = True

            cur2.execute(sqlCount)
            r = cur2.fetchone()
            self.view.setRowCount(int(r[0]))
            tableRow = 0
            cur.execute(sqlquery)
            for row in cur.fetchall():
                self.view.setItem(tableRow, 0, QTableWidgetItem(str(row[0])))
                self.view.setItem(tableRow, 1, QTableWidgetItem(str(row[1])))
                self.view.setItem(tableRow, 2, QTableWidgetItem(str(row[2])))
                self.view.setItem(tableRow, 3, QTableWidgetItem(str(row[3])))
                self.view.setItem(tableRow, 4, QTableWidgetItem(str(row[4])))
                self.view.setItem(tableRow, 5, QTableWidgetItem(row[5]))
                self.view.setItem(tableRow, 6, QTableWidgetItem(row[6]))

                tableRow += 1
        except sqlite3.Error as error:
            print("Failed to execute the above query", error)
        finally:
            if con:
                con.close()
    
    #update tables for one time
    def updateDatabaseReccuring(self, row, column):
        if not self.reccuring_flag:
            return
        try:
            con = sqlite3.connect("database.db")
            cur = con.cursor()

            # Fetch the values from the table
            id_item = self.view.item(row, 0)
            date_start_item = self.view.item(row, 1)
            date_stop_item = self.view.item(row, 2)
            time_start_item = self.view.item(row, 3)
            time_stop_item = self.view.item(row, 4)
            activity_item = self.view.item(row, 5)
            location_item = self.view.item(row, 6)
            

            id = id_item.text() if id_item else ''
            date_start = date_start_item.text() if date_start_item else ''
            date_stop = date_stop_item.text() if date_stop_item else ''
            time_start = time_start_item.text() if time_start_item else ''
            time_stop = time_stop_item.text() if time_stop_item else ''
            activity = activity_item.text() if activity_item else ''
            location = location_item.text() if location_item else ''

            # Assume the first column is the primary key or unique identifier
            # Update the database with the new values
            update_query = f"""
            UPDATE AppointmentsReccuring
            SET DateStart = "{str(date_start)}", DateStop = "{str(date_stop)}", TimeStart = "{str(time_start)}", TimeStop = "{str(time_stop)}", Activity = "{str(activity)}", Location = "{str(location)}"
            WHERE id = {int(id)}
            """
            #print(update_query)
            cur.execute(update_query) 
            con.commit()
        except sqlite3.Error as error:
            print("Failed to update the database", error)
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

            self.schedule_flag = False
            self.onetime_flag = False
            self.reccuring_flag = False

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

            tableRow = 0
            tableRowC = 0
            cur.execute(sqlquery)
            
            self.schedule_flag = False
            self.onetime_flag = False
            self.reccuring_flag = False

            for row in cur.fetchall():
                tableRowC += 1
            self.view.setRowCount(tableRowC)

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

            
        
        

        

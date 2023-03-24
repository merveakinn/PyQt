from shlex import join
from tabnanny import check
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

from os import getlogin, path
from configparser import ConfigParser
from time import sleep

class ProcessThread(QThread):
    isRunning = False
    send_error = pyqtSignal([str])
    
    def __init__(self, app):
        super(ProcessThread, self).__init__()
        self.app = app

    def run(self):
        while 1:
            if self.isRunning:
                config = ConfigParser()
                try: 
                    if path.exists(f"C:\\Users\\{getlogin()}\\Desktop\\Proje2\\orj_plasmac_7i76e.ini"): config.read(f"C:\\Users\\{getlogin()}\\Desktop\\Proje2\\orj_plasmac_7i76e.ini")
                    else: self.send_error.emit("Unable to find '.ini' file.")
                except Exception as e: self.send_error.emit(str(e))
                y1 = []
                y2 = []
                for jointname, joint in self.app.joints.items():
                    childs = joint.findChildren(QLineEdit)
                    for child in childs: 
                        if child.text().replace(" ","") == "": child.setText("0")

                    config.set(jointname, "P", childs[0].text())
                    config.set(jointname, "I", childs[1].text())
                    config.set(jointname, "D", childs[2].text())
                    config.set(jointname, "BIAS", childs[3].text())
                    config.set(jointname, "FF0", childs[4].text())
                    config.set(jointname, "FF1", childs[6].text())
                    config.set(jointname, "FF2", childs[6].text())
                    config.set(jointname, "DEADBAND", childs[7].text())
                    config.set(jointname, "MAX_OUTPUT", childs[8].text())
                    config.set(jointname, "DIRSETUP", childs[9].text())
                    config.set(jointname, "DIRHOLD", childs[10].text())
                    config.set(jointname, "STEPLEN", childs[11].text())
                    config.set(jointname, "STEPSPACE", childs[12].text())
                    config.set(jointname, "STEP_SCALE", childs[13].text())
                    config.set(jointname, "STEPGEN_MAXACCEL", childs[14].text())
                    config.set(jointname, "STEPGEN_MAXVEL", childs[15].text())
                    config.set(jointname, "HOME", childs[16].text())
                    config.set(jointname, "FERROR", childs[17].text())
                    config.set(jointname, "MIN_FERROR", childs[18].text())
                    config.set(jointname, "MAX_VELOCITY", childs[19].text())
                    config.set(jointname, "MAX_ACCELERATION", childs[20].text())
                    config.set(jointname, "MIN_LIMIT", childs[21].text())
                    config.set(jointname, "MAX_LIMIT", childs[22].text())
                    config.set(jointname, "BACKLASH", childs[23].text())
                    
                    if jointname == "JOINT_1":
                        for i in range(23): y1.append(childs[i].text())
                    elif jointname == "JOINT_2":
                        for i in range(23): y2.append(childs[i].text())

                    if jointname == "JOINT_0": axis = "AXIS_X"
                    elif jointname == "JOINT_1": axis = "AXIS_Y"
                    elif jointname == "JOINT_2": axis = "AXIS_Y"
                    elif jointname == "JOINT_3": axis = "AXIS_Z"
                    config.set(axis, "MAX_VELOCITY", childs[19].text())
                    config.set(axis, "MAX_ACCELERATION", childs[20].text())
                    config.set(axis, "MIN_LIMIT", childs[21].text())
                    config.set(axis, "MAX_LIMIT", childs[22].text())

                childs = self.app.traj.findChildren(QComboBox)+self.app.traj.findChildren(QLineEdit)+self.app.traj.findChildren(QCheckBox)
                for child in childs: 
                    try:
                        if child.text().replace(" ","") == "" and type(child) != QCheckBox: child.setText("0")
                    except: pass
                config.set("TRAJ", "LINEAR_UNITS", childs[0].currentText())
                config.set("TRAJ", "DEFAULT_LINEAR_VELOCITY", childs[1].text())
                config.set("TRAJ", "MAX_LINEAR_VELOCITY", childs[2].text())
                checkval = "1" if childs[3].isChecked() == True else "0"
                config.set("TRAJ", "NO_FORCE_HOMING", checkval)

                with open(f"C:\\Users\\{getlogin()}\\Desktop\\Proje2\\orj_plasmac_7i76e.ini", "w") as f: config.write(f)

                self.app.getVals()

                self.app.save.setText("Save To File")
                self.app.save.setEnabled(True)

                if y1 != y2: 
                    self.send_error.emit("JOINT_1 doesn't match JOINT_2.")
                sleep(0.1)

                self.app.canMessage = True
                self.isRunning = False
            sleep(0.5)

class MainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.title = "Calibrator"
        self.setWindowTitle(self.title)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.canMessage = True
        layout = QGridLayout()
        self.setLayout(layout)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 0, 0)

        self.joint0 = QFrame()
        joint0grid = QVBoxLayout()
        self.joint0.setLayout(joint0grid)
        self.tabs.addTab(self.joint0, "JOINT_0")
        self.loadTab(self.joint0)

        self.joint1 = QFrame()
        joint1grid = QVBoxLayout()
        self.joint1.setLayout(joint1grid)
        self.tabs.addTab(self.joint1, "JOINT_1")
        self.loadTab(self.joint1)

        self.joint2 = QFrame()
        joint2grid = QVBoxLayout()
        self.joint2.setLayout(joint2grid)
        self.tabs.addTab(self.joint2, "JOINT_2")
        self.loadTab(self.joint2, True)

        self.joint3 = QFrame()
        joint3grid = QVBoxLayout()
        self.joint3.setLayout(joint3grid)
        self.tabs.addTab(self.joint3, "JOINT_3")
        self.loadTab(self.joint3)

        self.traj = QFrame()
        trajgrid = QVBoxLayout()
        self.traj.setLayout(trajgrid)
        self.tabs.addTab(self.traj, "TRAJ")
        self.loadTraj()

        self.save = QPushButton("Save To File")
        self.save.setFixedHeight(30)
        self.save.clicked.connect(self.saveVals)
        layout.addWidget(self.save, 1, 0)

        self.joints = {"JOINT_0":self.joint0, "JOINT_1":self.joint1, "JOINT_2":self.joint2, "JOINT_3":self.joint3}

        self.myStyle()
        self.procThread = ProcessThread(self)
        self.procThread.send_error.connect(self.onError)
        self.procThread.start()

        self.getVals()

    def onError(self, message="Test Message"): 
        if self.canMessage: QMessageBox.about(self, f"{self.title}", message)

    def getj1(self):
        joint1Edits = self.joint1.findChildren(QLineEdit)
        joint2Edits = self.joint2.findChildren(QLineEdit)
        for i in range(len(joint1Edits)):
            joint2Edits[i].setText(joint1Edits[i].text())

    def getVals(self):
        config = ConfigParser()
        try: 
            if path.exists(f"C:\\Users\\{getlogin()}\\Desktop\\Proje2\\orj_plasmac_7i76e.ini"): config.read(f"C:\\Users\\{getlogin()}\\Desktop\\Proje2\\orj_plasmac_7i76e.ini")
            else: self.onError("Unable to find '.ini' file.")
        except Exception as e: self.onError(str(e))

        for jointname, joint in self.joints.items():
            childs = joint.findChildren(QLineEdit)
            for child in childs: 
                if child.text().replace(" ","") == "": child.setText("0")

            childs[0].setText(config.get(jointname, "P"))
            childs[1].setText(config.get(jointname, "I"))
            childs[2].setText(config.get(jointname, "D"))
            childs[3].setText(config.get(jointname, "BIAS"))
            childs[4].setText(config.get(jointname, "FF0"))
            childs[5].setText(config.get(jointname, "FF1"))
            childs[6].setText(config.get(jointname, "FF2"))
            childs[7].setText(config.get(jointname, "DEADBAND"))
            childs[8].setText(config.get(jointname, "MAX_OUTPUT"))
            childs[9].setText(config.get(jointname, "DIRSETUP"))
            childs[10].setText(config.get(jointname, "DIRHOLD"))
            childs[11].setText(config.get(jointname, "STEPLEN"))
            childs[12].setText(config.get(jointname, "STEPSPACE"))
            childs[13].setText(config.get(jointname, "STEP_SCALE"))
            childs[14].setText(config.get(jointname, "STEPGEN_MAXACCEL"))
            childs[15].setText(config.get(jointname, "STEPGEN_MAXVEL"))
            childs[16].setText(config.get(jointname, "HOME"))
            childs[17].setText(config.get(jointname, "FERROR"))
            childs[18].setText(config.get(jointname, "MIN_FERROR"))
            childs[19].setText(config.get(jointname, "MAX_VELOCITY"))
            childs[20].setText(config.get(jointname, "MAX_ACCELERATION"))
            childs[21].setText(config.get(jointname, "MIN_LIMIT"))
            childs[22].setText(config.get(jointname, "MAX_LIMIT"))
            childs[23].setText(config.get(jointname, "BACKLASH"))

            childs = joint.findChildren(QLabel, "halval")

            childs[0].setText(config.get(jointname, "P"))
            childs[1].setText(config.get(jointname, "I"))
            childs[2].setText(config.get(jointname, "D"))
            childs[3].setText(config.get(jointname, "BIAS"))
            childs[4].setText(config.get(jointname, "FF0"))
            childs[5].setText(config.get(jointname, "FF1"))
            childs[6].setText(config.get(jointname, "FF2"))
            childs[7].setText(config.get(jointname, "DEADBAND"))
            childs[8].setText(config.get(jointname, "MAX_OUTPUT"))
            childs[9].setText(config.get(jointname, "DIRSETUP"))
            childs[10].setText(config.get(jointname, "DIRHOLD"))
            childs[11].setText(config.get(jointname, "STEPLEN"))
            childs[12].setText(config.get(jointname, "STEPSPACE"))
            childs[13].setText(config.get(jointname, "STEP_SCALE"))
            childs[14].setText(config.get(jointname, "STEPGEN_MAXACCEL"))
            childs[15].setText(config.get(jointname, "STEPGEN_MAXVEL"))
            childs[16].setText(config.get(jointname, "HOME"))
            childs[17].setText(config.get(jointname, "FERROR"))
            childs[18].setText(config.get(jointname, "MIN_FERROR"))
            childs[19].setText(config.get(jointname, "MAX_VELOCITY"))
            childs[20].setText(config.get(jointname, "MAX_ACCELERATION"))
            childs[21].setText(config.get(jointname, "MIN_LIMIT"))
            childs[22].setText(config.get(jointname, "MAX_LIMIT"))
            childs[23].setText(config.get(jointname, "BACKLASH"))

        childs = self.traj.findChildren(QComboBox)+self.traj.findChildren(QLineEdit)+self.traj.findChildren(QCheckBox)+self.traj.findChildren(QLabel, "halval")
        for child in childs: 
            try:
                if child.text().replace(" ","") == "" and type(child) != QCheckBox: child.setText("0")
            except: pass

        lin_u = 0 if config.get("TRAJ", "LINEAR_UNITS").strip().lower() == "mm" else 1
        childs[0].setCurrentIndex(lin_u)
        childs[1].setText(config.get("TRAJ", "DEFAULT_LINEAR_VELOCITY"))
        childs[2].setText(config.get("TRAJ", "MAX_LINEAR_VELOCITY"))
        checkval = True if config.get("TRAJ", "NO_FORCE_HOMING") == "1" else False
        childs[3].setChecked(checkval)
        childs[4].setText(config.get("TRAJ", "LINEAR_UNITS"))
        childs[5].setText(config.get("TRAJ", "DEFAULT_LINEAR_VELOCITY"))
        childs[6].setText(config.get("TRAJ", "MAX_LINEAR_VELOCITY"))
        childs[7].setText(config.get("TRAJ", "NO_FORCE_HOMING"))

    def setMaxVel(self):
        tab = self.tabs.currentWidget()
        childs = tab.findChildren(QLineEdit)
        if tab in self.joints.values():
            config = ConfigParser()
            try:
                val = float(childs[19].text())
                childs[15].setText(str(round(val*1.25, 7)))
                #childs[14].setText(str(round(val*1.25, 7)))
            except Exception as e: self.onError(str(e))
        self.saveVals(False)
            
    def setMaxAcc(self):
        tab = self.tabs.currentWidget()
        childs = tab.findChildren(QLineEdit)
        if tab in self.joints.values():
            config = ConfigParser()
            try: 
                val = float(childs[20].text())
                childs[14].setText(str(round(val*1.25, 7)))
                #childs[15].setText(str(round(val*1.25, 7)))
            except Exception as e: self.onError(str(e))
        self.saveVals(False)
            
    def saveVals(self, cm=True):
        if self.procThread.isRunning: self.save.setText("Save To File"), self.save.setEnabled(True)
        else:
            self.canMessage = cm
            self.save.setText("Saving"), self.save.setEnabled(False)
        self.procThread.isRunning = not self.procThread.isRunning

    def loadTraj(self):
        self.addTitles(self.traj, "INI Name", "HAL's Value", "Next Value")
        self.addVariable(self.traj, "LINEAR_UNITS", True)
        self.addVariable(self.traj, "DEFAULT_LINEAR_VELCTY", True)
        self.addVariable(self.traj, "MAX_LINEAR_VELOCITY", True)
        self.addVariable(self.traj, "FORCE_HOME", True)
        #self.traj.layout().addWidget(self.tfram)
        self.addButtons(self.traj, False, True)

    def loadTab(self, tab, j2=False):
        self.addTitles(tab, "INI Name", "HAL's Value", "Next Value")
        self.addVariable(tab, "P")
        self.addVariable(tab, "I")
        self.addVariable(tab, "D")
        self.addVariable(tab, "BIAS")
        self.addVariable(tab, "FF0")
        self.addVariable(tab, "FF1")
        self.addVariable(tab, "FF2")
        self.addVariable(tab, "DEADBAND")
        self.addVariable(tab, "MAX_OUTPUT")
        self.addVariable(tab, "DIRSETUP")
        self.addVariable(tab, "DIRHOLD")
        self.addVariable(tab, "STEPLEN")
        self.addVariable(tab, "STEPSPACE")
        self.addVariable(tab, "STEP_SCALE")
        self.addVariable(tab, "STEPGEN_MAXACCEL")
        self.addVariable(tab, "STEPGEN_MAXVEL")
        self.addVariable(tab, "HOME")
        self.addVariable(tab, "FERROR")
        self.addVariable(tab, "MIN_FERROR")
        self.addVariable(tab, "MAX_VELOCITY")
        self.addVariable(tab, "MAX_ACCELERATION")
        self.addVariable(tab, "MIN_LIMIT")
        self.addVariable(tab, "MAX_LIMIT")
        self.addVariable(tab, "BACKLASH")
        self.addButtons(tab, j2)

    def addButtons(self, tab, j2=False, traj=False):
        widget = QWidget()
        grid = QHBoxLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0,0,0,0)
        widget.setLayout(grid)
        if j2: 
            getj1 = QPushButton("Get JOINT_1")
            getj1.setFixedHeight(30)
            getj1.setFixedWidth(120)
            getj1.clicked.connect(self.getj1)
            grid.addWidget(getj1)
        refresh = QPushButton("Refresh", objectName="traj" if traj else "btn")
        refresh.clicked.connect(self.getVals)
        refresh.setFixedHeight(30)
        #refresh.setFixedWidth(70)
        grid.addWidget(refresh)
        tab.layout().addWidget(widget)

    def addTitles(self, tab, *titles):
        widget = QWidget()
        grid = QHBoxLayout()
        grid.setContentsMargins(0,0,0,0)
        widget.setLayout(grid)
        for i in titles: 
            label = QLabel(i)
            label.setAlignment(Qt.AlignCenter)
            grid.addWidget(label)
        tab.layout().addWidget(widget)

    def addVariable(self, tab, var, traj=False):
        widget = QWidget()
        grid = QHBoxLayout()
        grid.setContentsMargins(0,0,0,0)
        grid.setSpacing(50)
        widget.setLayout(grid)
        name = QLabel(var+":")
        name.setAlignment(Qt.AlignRight)
        name.setFixedWidth(135)
        name.setFixedHeight(15)
        hal = QLabel("_", objectName="halval")
        hal.setAlignment(Qt.AlignRight)
        hal.setFixedHeight(15)
        next = QLineEdit()
        grid.addWidget(name)
        grid.addWidget(hal)
        if var == "STEPGEN_MAXVEL":
            grid.setSpacing(0)
            setmxvl = QPushButton("Autoset")
            setmxvl.setFixedHeight(20)
            setmxvl.setFixedWidth(50)
            setmxvl.clicked.connect(self.setMaxVel)
            grid.addWidget(setmxvl)
        if var == "STEPGEN_MAXACCEL":
            grid.setSpacing(0)
            setmxac = QPushButton("Autoset")
            setmxac.setFixedHeight(20)
            setmxac.setFixedWidth(50)
            setmxac.clicked.connect(self.setMaxAcc)
            grid.addWidget(setmxac)
        if var == "LINEAR_UNITS":
            next = QComboBox()
            next.addItems(("mm", "inch"))
        if var == "FORCE_HOME":
            next = QCheckBox()
        next.setFixedWidth(100)
        next.setFixedHeight(15)
        grid.addWidget(next)
        if traj: tab.layout().setAlignment(Qt.AlignTop)
        tab.layout().addWidget(widget)

    def myStyle(self):
        self.css = """
        
        QLabel {
            font-family: Segoe UI;
            font-size: 11px;
            color: black;
        }

        QLabel#halval {
            font-family: Segoe UI;
            font-size: 11px;
            color: #AB3525;
        }

        QLineEdit {
            font-family: Segoe UI;
            font-size: 11px;
            color: black;
        }

        QPushButton#traj {
            
        }

        """

        self.setStyleSheet(self.css)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWidget()
    root.show()
    root.setFixedSize(QSize(420, root.height()))
    sys.exit(app.exec_())

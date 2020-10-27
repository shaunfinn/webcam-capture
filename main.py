

import cv2
import time
import config

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QMainWindow
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QImage, QPixmap

# https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv/44404713

#  this works with Qthread but not sure how to stop and restart thread

class Worker(QObject):
    changePixmap = pyqtSignal(QImage)
    changeFps = pyqtSignal(str)

    @pyqtSlot(bool, bool)
    def start_capture(self, stream, write):
        print( "start capture: streaming=",  stream, " writing=", write)
        cap = cv2.VideoCapture(0)

        if write:
            # Define the codec and create VideoWriter object (XVID- default codec)
            fourcc = cv2.VideoWriter_fourcc(*'FFV1')
            out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

        config.capture = True
        cnt = 0  #frame count
        t_start = time.time()
        while config.capture:
            ret, frame = cap.read()
            if ret:
                cnt+=1
                #Streaming to GUI
                if stream :
                    # https://stackoverflow.com/a/55468544/6622587
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                #Writing to file
                if write:
                    out.write(frame)

                #calculate frame rate and display in GUI, updates every 50 frames
                if cnt % 50 == 0:
                    fps = str(round(cnt/(time.time()-t_start ),1))
                    # print( "fps:", cnt / (time.time()-t_start ))
                    self.changeFps.emit(fps)

        # Release everything if job is finished
        cap.release()
        if write:
            out.release()
        #cv2.destroyAllWindows()
        #print("stop cap trigger ", time.time())

    @pyqtSlot()
    def start_video(self):

        #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#saving-a-video
        cap = cv2.VideoCapture(0)



        config.capture = True
        cnt = 0  #frame count
        t_start = time.time()

        while config.capture:
            ret, frame = cap.read()
            if ret:
                cnt+=1
                # write the flipped frame
                out.write(frame)

                # calculate frame rate, updates every 50 frames
                if cnt % 50 == 0:
                    fps = str(round(cnt / (time.time() - t_start), 1))
                    # print( "fps:", cnt / (time.time()-t_start ))
                    self.changeFps.emit(fps)

        # Release everything if job is finished
        cap.release()
        out.release()
        #cv2.destroyAllWindows()





class MyWindow(QMainWindow):
    
    capture_start = pyqtSignal(bool,bool)
    video_start = pyqtSignal()
    
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('gui.ui', self)
        #self.show()
        
        self.b_start.clicked.connect(self.m_startcap)
        self.b_stop.clicked.connect(self.m_stopcap)

        # self.th = Thread(self)
        # self.th.changePixmap.connect(self.setImage)


        #self.stepper = stepperControl()
        
        # Create a worker object and a thread
        self.worker = Worker()
        self.worker_thread = QThread()
        # Assign the worker to the thread and start the thread
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        # Connect signals & slots AFTER moving the object to the thread
        self.capture_start.connect(self.worker.start_capture)
        self.video_start.connect(self.worker.start_video)
        self.worker.changePixmap.connect(self.setImage)
        self.worker.changeFps.connect(self.setFps)

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.l_img.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(str)
    def setFps(self, fps):
        self.l_fps.setText(fps)
        
    def m_startcap(self):
        # config.capture = True
        print("start capture")
        stream = self.ch_stream.isChecked()
        write = self.ch_write.isChecked()
        self.capture_start.emit(stream, write)
        #self.video_start.emit()
    
    def m_stopcap(self):
        #print("stop cap trigger ", time.time())
        config.capture = False


if __name__ == "__main__":
    app = QApplication([])
    win = MyWindow()
    win.show()
    app.exec_()
    

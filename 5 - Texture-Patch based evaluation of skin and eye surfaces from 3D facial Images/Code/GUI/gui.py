import os 
import cv2
import sys 
import joblib
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore
from sklearn.neighbors import KNeighborsClassifier
os.chdir("Code//")

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
    print("Path appended")
from Image.Processor import Utils, Eye
class ImageWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Load KNN model 
        self.knn = joblib.load("Image//classifiers//knn.joblib")


        # Set Window Size 
        self.setGeometry( 100, 100, 1280, 720 )

        # Create a layout
        layout = QtWidgets.QHBoxLayout(self)
        self.setWindowTitle("Sclera Analyser")
        # Create an image container
        image_container = QtWidgets.QFrame()
        image_container.setFrameShape(QtWidgets.QFrame.StyledPanel)
        layout.addWidget(image_container, stretch=50)

        # Create a vertical layout for the image container
        container_layout = QtWidgets.QVBoxLayout()
        image_container.setLayout(container_layout)

        # Create a drag-and-drop image box
        self.image_box = QtWidgets.QLabel()
        self.image_box.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.image_box.setAcceptDrops(True)
        container_layout.addWidget(self.image_box)

        # Create an open image button
        open_image_button = QtWidgets.QPushButton("Open Image")
        open_image_button.clicked.connect(self.open_image)
        container_layout.addWidget(open_image_button)

        # Create a rotate image button
        rotate_image_button = QtWidgets.QPushButton("Rotate Image")
        container_layout.addWidget(rotate_image_button)

        # Connect the rotate image button to the rotate_image method
        rotate_image_button.clicked.connect(self.rotate_image)

        # Create a horizontal line as a separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(separator)

        # Create an empty horizontal box with a purple background
        self.empty_box = QtWidgets.QFrame()
        self.empty_box.setStyleSheet("background-color: #b0c6eb;")
        layout.addWidget(self.empty_box, stretch=50)
        self.empty_box.hide()
        # Create a grid layout for the empty box
        grid_layout = QtWidgets.QGridLayout()
        self.empty_box.setLayout(grid_layout)

        # Create two image boxes
        self.image_box1 = QtWidgets.QLabel()
        self.image_box2 = QtWidgets.QLabel()
        self.image_box3 = QtWidgets.QLabel()
        self.image_box4 = QtWidgets.QLabel()
        self.text_box1 = QtWidgets.QLabel()
        self.text_box2 = QtWidgets.QLabel()
        grid_layout.addWidget(self.image_box1, 0, 0)
        grid_layout.addWidget(self.image_box3, 0, 1)
        grid_layout.addWidget(self.text_box1, 0, 2)
        grid_layout.addWidget(self.image_box2, 1, 0)
        grid_layout.addWidget(self.image_box4, 1, 1)
        grid_layout.addWidget(self.text_box2, 1, 2)
        # Scale the contents of the image boxes
        self.image_box1.setScaledContents(True)
        self.image_box2.setScaledContents(True)
        self.image_box3.setScaledContents(True)
        self.image_box4.setScaledContents(True)
        # Set the layout
        self.setLayout(layout)

    def rotate_image(self):
        # Rotate the pixmap of the image box by 90 degrees
        pixmap = self.image_box.pixmap()
        transform = QtGui.QTransform().rotate(90)
        pixmap = pixmap.transformed(transform)
        self.image_box.setPixmap(pixmap)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # Get the first URL from the list of dropped URLs
            url = event.mimeData().urls()[0].toLocalFile()
            # Load the image
            pixmap = QtGui.QPixmap(url)
            # Rescale the image to 50% of the window width
            pixmap = pixmap.scaledToWidth(self.image_box.width() / 2, QtCore.Qt.SmoothTransformation)
            # Display the image in the image box
            self.image_box.setPixmap(pixmap)


    def number_label(self, num):
        text = ""
        if num == 0: 
            text = "Signs of Jaundice"
        elif num == 1:
            text = "Normal Sclera"
        elif num == 2: 
            text = "Signs of Osteogensis Imperfecta"
        return text 

    def set_image(self, img_path, image_box, width=250, height=100):
        if width >= 400: 
            width = width / 2 
            height = height / 2 

        
        load_img = QtGui.QPixmap(img_path)
        image_box.setFixedSize(width, height)
        scaled = load_img.scaled(image_box.size(), QtCore.Qt.KeepAspectRatio )
        image_box.setPixmap(scaled)



    def open_image(self):
        # Open a file dialog to select an image
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options
        )
        if file_name:
            print(file_name)
            o_l, o_r, l_s, r_s = Eye.Face_To_LR_Sclera(file_name, retrieveCrops=True)

            l_s_h = Utils.Image_To_Histogram(  l_s, concat=True  ).flatten() 
            r_s_h = Utils.Image_To_Histogram(  r_s, concat=True  ).flatten() 

            prediction_left  = self.knn.predict( l_s_h.reshape(1,-1) )[0]
            prediction_right = self.knn.predict( r_s_h.reshape(1,-1) )[0]

            prediction_left = self.number_label(prediction_left)
            prediction_right = self.number_label(prediction_right)

            self.empty_box.show()
            self.text_box1.setText(prediction_left)
            self.text_box2.setText(prediction_right)

            Utils.Save_image( o_l, "GUI//.temp//o_l.png" )
            Utils.Save_image( o_r, "GUI//.temp//o_r.png" )
            Utils.Save_image( l_s, "GUI//.temp//l_s.png" )
            Utils.Save_image( r_s, "GUI//.temp//r_s.png" )

            self.set_image("GUI//.temp//o_l.png", self.image_box1, width=250, height=100)
            self.set_image("GUI//.temp//o_r.png", self.image_box2, width=250, height=100)
            self.set_image("GUI//.temp//l_s.png", self.image_box3, width=250, height=100)
            self.set_image("GUI//.temp//r_s.png", self.image_box4, width=250, height=100)

            
            print(self.image_box1.size)
            # Load the image
            pixmap = QtGui.QPixmap(file_name)
            # Rotate the image
            #pixmap = pixmap.transformed(QtGui.QTransform().rotate(270))

            # Scale the image to the size of the container
            scaled_pixmap = pixmap.scaled(self.image_box.size(), QtCore.Qt.KeepAspectRatio)

            # Display the scaled image in the image box
            self.image_box.setPixmap(scaled_pixmap)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ImageWindow()
    app.setStyleSheet("QLabel{font-size: 18pt;}")

    
    window.show()
    sys.exit(app.exec_())
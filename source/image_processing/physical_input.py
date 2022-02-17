from genericpath import isdir
from PIL import ImageGrab, Image
import win32gui
import psutil
import win32process
import pywinauto
from pynput.keyboard import Key, Controller
from ctypes import windll
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import os

class ProcessImage:
    def __init__(self, proc_name):
        # disable display scaling for this app - fixes the 
        # issue of image grab being in the wrong place
        user32 = windll.user32
        user32.SetProcessDPIAware()

        self.ProcessName = proc_name + '.exe'
        self.WindowImage = None
        self.Succeeded = False
        self.Hwnd, self.WindowImage = self.get_wind_image_by_name(proc_name)
        #self.show_window_img(self.WindowImage)
        self.Succeeded = True

    # format PIL Image type to image for opencv which is BGR
    def format_BGR(self):
        pil_image = self.WindowImage.convert('RGB') 
        open_cv_image = np.array(pil_image) 
        # Convert RGB to BGR 
        return cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)

    def show_window_img(self, img):
        img.show()

    def get_wind_image_by_name(self, proc_name):
        hwnd = self.__find_hwnd_by_name(proc_name)
        if hwnd is None: return None, None
        return  hwnd, self.__get_wind_image(hwnd)

    def __get_wind_image(self, hwnd):
        win32gui.SetForegroundWindow(hwnd)
        self.ImageBoundingBox = win32gui.GetWindowRect(hwnd)
        img = ImageGrab.grab(self.ImageBoundingBox)
        return img

    def __find_hwnd_by_name(self, proc_name):
        def callback(hwnd, hwnds):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                nID = win32process.GetWindowThreadProcessId(hwnd)
                del nID[0]
                for pid in nID:
                    name = psutil.Process(pid).name()
                    if proc_name in name: hwnds.append(hwnd)

            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)

        if not any(hwnds): return None
        return hwnds[0]

class PhysicalInput:
    def __init__(self, img : ProcessImage):
        # create directory for template images
        self.ImageTemplateDir = os.path.realpath('.').replace("\\", "/") + '/template_images'
        self.__create_template_image_directory(self.ImageTemplateDir)

        #run matching and look for button
        self.ProcessWindowImage = img

    def __create_template_image_directory(self, dir_path):
        is_dir = os.path.isdir(dir_path)
        if not is_dir:
            os.mkdir(dir_path)
            print("Image template directory created at -> {}".format(dir_path))

    def __get_template_img_path(self, img_name):
        img_path = self.ImageTemplateDir + '/' + img_name
        is_file = os.path.isfile(img_path)
        if not is_file:
            print("Image template file not found at -> {}".format(img_path))
            return None
        return img_path

    # format image file for opencv which is BGR
    def __format_BGR(self, img_path : str):
        pil_image = Image.open(img_path).convert('RGB')
        open_cv_image = np.array(pil_image) 
        # Convert RGB to BGR 
        return cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)

    def run_MSER(self):
        img = self.ProcessWindowImage.get_opencv_format_img()
        vis = img.copy()
        mser = cv.MSER_create()
        msers, regions = mser.detectRegions(img)
        hulls = [cv.convexHull(p.reshape(-1, 1, 2)) for p in msers]
        cv.polylines(vis, hulls, 1, (0, 255, 0))
        cv.imshow('img', vis)
        cv.waitKey(0)
        cv.destroyAllWindows()

    # uses template matching provided a template image of a button to locate said button
    # on a GUI window and return the coordinates of the center of that button
    def get_button_coord_from_template(self, template_img_name):
        template_img_path = self.__get_template_img_path(template_img_name)
        if template_img_path is None: return
        template = self.__format_BGR(template_img_path)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

        img = self.ProcessWindowImage.format_BGR()
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img2 = img.copy()
        w, h = template.shape[::-1]
        
        # methods in comment below can be used as well
        #'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR','cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED'
        meth = 'cv.TM_CCOEFF'
        img = img2.copy()
        method = eval(meth)

        # Apply template Matching
        res = cv.matchTemplate(img,template,method)
        _, _, _, max_loc = cv.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center_offset = (int((bottom_right[0] + top_left[0]) / 2), int((bottom_right[1] + top_left[1]) / 2))
        # cv.circle(img, center, radius=1, color=(0, 0, 255), thickness=3)
        # plt.plot(),plt.imshow(img,cmap = 'gray')
        # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        # plt.suptitle(meth)
        # plt.show()
        return center_offset

    def click_at_coords(self, pt):
        app = pywinauto.Application().connect(path=self.ProcessWindowImage.ProcessName)
        app.top_window().click_input(coords=pt)

    def send_str(self, txt: str):
        keyboard = Controller()
        keys = [c for c in txt]
        for key in keys:
            keyboard.press(key)
            keyboard.release(key)

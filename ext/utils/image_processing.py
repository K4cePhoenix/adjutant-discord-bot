from PIL import Image, ImageChops, ImageOps
from matplotlib import pyplot as plt
import cv2
import numpy as np
import requests

from io import BytesIO

async def url_to_image(self, url):
    r = requests.get(url)
    img = Image.open(BytesIO(r.content))
    img = img.resize((512, 512,), resample=Image.LANCZOS)
    return img

def pil2ocv(img):
    cv2_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)
    return cv2_img

def ocv2pil(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img)
    return pil_img

def invert_image(img):
    if img.mode == 'RGBA':
        r,g,b,a = img.split()
        rgb_img = Image.merge('RGB', (r,g,b))
        inv_img = ImageOps.invert(rgb_img)
        r2,g2,b2 = inv_img.split()
        ret_img = Image.merge('RGBA', (r2,g2,b2,a))
    elif img.mode == 'RGB':
        ret_img = ImageChops.invert(img)
    else:
        ret_img = ImageOps.invert(img)
    return ret_img

def greyscale_image(img):
    ret_img = img.convert(mode='L')
    return ret_img

def websafe(img):
    img = img.convert(mode='RGB')
    ret_img = ImageOps.posterize(img, bits=3)
    return ret_img

def smooth(img, _type):
    if _type == "average":
        tmp_img = pil2ocv(img)
        tmp_img = cv2.blur(tmp_img, (5,5))
        ret_img = ocv2pil(tmp_img)
    elif _type == "gaussian":
        tmp_img = pil2ocv(img)
        tmp_img = cv2.GaussianBlur(tmp_img,(5,5),0)
        ret_img = ocv2pil(tmp_img)
    elif _type == "median":
        tmp_img = pil2ocv(img)
        tmp_img = cv2.medianBlur(tmp_img,5)
        ret_img = ocv2pil(tmp_img)
    else:
        ret_img = img
    return ret_img

def hist_equalise(img):
    if img.mode == 'RGBA':
        r,g,b,a = img.split()
        rgb_img = Image.merge('RGB', (r,g,b))
        inv_img = ImageOps.equalize(rgb_img)
        r2,g2,b2 = inv_img.split()
        ret_img = Image.merge('RGBA', (r2,g2,b2,a))
    elif img.mode == 'RGB':
        ret_img = ImageChops.equalize(img)
    else:
        ret_img = ImageOps.equalize(img)
    return ret_img

def histogram(img, u, lg=True):
    if img.mode == 'RGBA':
        img = img.convert(mode='RGB')
        bins = range(0,256)
        hist = img.histogram()
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1, xlabel='Grey value', ylabel='Quantity', label=f"Histogram for Avator of {u.name}")
        plot_img = ax.plot(bins, hist[0:256], 'r', bins, hist[256:256+256], 'g', bins, hist[256+256:256+256+256], 'b')
        if lg:
            ax.set_yscale('log')
        tmp_file = BytesIO()
        plt.savefig(tmp_file, format='png')
        ret_img = Image.open(tmp_file)
        ax.clear()
        fig.clear()
    elif img.mode == 'RGB':
        bins = range(0,256)
        hist = img.histogram()
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1, xlabel='Grey value', ylabel='Quantity', label=f"Histogram for Avator of {u.name}")
        plot_img = ax.plot(bins, hist[0:256], 'r', bins, hist[256:256+256], 'g', bins, hist[256+256:256+256+256], 'b')
        if lg:
            ax.set_yscale('log')
        tmp_file = BytesIO()
        plt.savefig(tmp_file, format='png')
        ret_img = Image.open(tmp_file)
        ax.clear()
        fig.clear()
    elif img.mode == 'L':
        bins = range(0,256)
        hist = img.histogram()
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1, xlabel='Grey value', ylabel='Quantity', label=f"Histogram for Avator of {u.name}")
        plot_img = ax.plot(bins, hist[0:256], 'k')
        if lg:
            ax.set_yscale('log')
        tmp_file = BytesIO()
        plt.savefig(tmp_file, format='png')
        ret_img = Image.open(tmp_file)
        ax.clear()
        fig.clear()
    else:
        ret_img = img
    return ret_img

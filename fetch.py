# -*- coding: utf-8 -*-
"""
Script to grab all these huge highrise images
from remote server, store them locally.
cut them into wierd pieces for feeding to browser
"""
# import Image
import sys
import os
import requests
from types import FunctionType
from json import load, dumps
from time import sleep
from random import randint
from jinja2 import Template
from PIL import Image, ImageOps
from config import IMG_CROP_SIZE, DATA_FILE_NAME, RAW_IMG_PATH, CROPPED_IMG_PATH

class ImagePipeline():

    data_file = DATA_FILE_NAME
    img_path = CROPPED_IMG_PATH
    raw_img_path = RAW_IMG_PATH
    image_crop_size = IMG_CROP_SIZE

    def __init__(self):
        with open(self.data_file) as f:
            self.data = load(f)

        self.all_image_filenames = []  # util
        for (dirpath, dirnames, filenames) in os.walk(self.raw_img_path):
            for f in filenames:
                if 'jpg' in f or 'png' in f:
                    self.all_image_filenames.append(f)

    def __read_json_file__(self):
        """ edit this method to customize for various json schema
            grab the url and image filename to save locally for this img
            returns a dict """
        # json to dict
        images = []
        for img in self.data['objects']:
            url = img['img_url']
            img_filename = url.split('/')[-1]
            images.append({'url': url, 'img_filename': img_filename})
        return images

    def __random_shape__(self, img):
        """ returns a randomly selected shape in a 4 tuple of coordinates
            img is an object with: img.width, img.height  """
        all_areas = [
            (0, 0, 800, 800),  # big square 1
            (0, 0, 400, 400),  # square 1
            (400, 0, 800, 400),  # square 2
            (0, 400, 400, 800),  # square 3
            (400, 400, 800, 800),  # square 4
            (0, 0, 400, 800),  # long vert 1
            (400, 0, 800, 800),  # long vert 2
            (0, 0, 800, 400),  # long horiz 1
            (0, 400, 800, 800),  # long horiz 1
            ]
        area = all_areas[randint(0,len(all_areas)-1)]
        return area

    def fetch(self):
        """ reads image urls from json data_file and
            fetches images from remote server then saves
            them locally inside raw_img_path
            """
        for img_info in self.__read_json_file__():
            url = img_info['url']
            img_filename = img_info['img_filename']
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(self.raw_img_path + img_filename, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
                    print("saved: {}".format(img_filename))
            sleep(randint(0,3))

    def create(self):
        """ create thumbnails of all images """

        for img_name in self.all_image_filenames:
            img = Image.open("{}{}".format(self.raw_img_path, img_name))
            # we want 400 px wide images in browser, 3 times that for retina
            if img.width >=  self.image_crop_size[0] and img.height >=  self.image_crop_size[1]:

                # save the image in a new size
                thumb = ImageOps.fit(img, self.image_crop_size, Image.ANTIALIAS)
                print("cropping {} to {}".format(img_name, str(self.image_crop_size)))
                thumb.save("{}{}".format(self.img_path, img_name))

            else:
                print("{} too small at {}x{}".format(img_name, str(img.width), str(img.height) ))

    def shapes(self):
        """ create a crop of each image in one of the random shapes() """

        for img_name in self.all_image_filenames:
            img = Image.open("{}{}".format(self.raw_img_path, img_name))
            # we want 400 px wide images in browser, 3 times that for retina
            if img.width >=  self.image_crop_size[0] and img.height >=  self.image_crop_size[1]:

                shape = self.__random_shape__(img)
                shape = (0,0,800,800)
                img.crop(shape).save("{}{}".format(self.img_path, img_name))

            else:
                print("{} too small at {}x{}".format(img_name, str(img.width), str(img.height) ))


    def html(self):
        """ prints html of images list to stdout """

        template = Template("""
            <ul>
                {% for filename in all_image_filenames %}
                    <li><img src="{{ img_path }}{{ filename }}"></li>
                {% endfor %}
            </ul>
            """)
        t = template.render(img_path=self.img_path, all_image_filenames=self.all_image_filenames)
        print(t)

    def json(self):
        """ prints json list of image urls to stdout """

        print(dumps({'data': self.all_image_filenames}))


if __name__ == '__main__':

    image_maker = ImagePipeline();
    class_methods = [attr for attr in dir(image_maker) if callable(getattr(image_maker, attr)) and not attr.startswith("__")]

    fail_msg = """

                      Please specify fetch or crop: \n

                      python images.py <{}>

                     """.format('/'.join(class_methods))
    try:
        action = sys.argv[1]
    except IndexError as err:
        print(err)
        # print(fail_msg)

    try:
        method = getattr(image_maker, action)
        method()
    except AttributeError as err:
        # print(err)
        print(fail_msg)

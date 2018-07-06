# -*- coding: utf-8 -*-
"""
Script to grab all these huge highrise images
from remote server, store them locally.
cut them into wierd pieces for feeding to browser
"""
# import Image
import sys
import os
import json
import requests
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
            self.data = json.load(f)

        self.all_image_filenames = []  # util
        for (dirpath, dirnames, filenames) in os.walk(self.raw_img_path):
            for f in filenames:
                if 'jpg' in f or 'png' in f:
                    self.all_image_filenames.append(f)

    def read_json_file(self):
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

    def fetch_images(self):
        """ reads image urls from json data_file and
            fetches images from remote server then saves
            them locally inside raw_img_path
            """
        for img_info in self.read_json_file():
            url = img_info['url']
            img_filename = img_info['img_filename']
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(self.raw_img_path + img_filename, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
                    print("saved: {}".format(img_filename))
            sleep(randint(0,3))

    def create_thumbnails(self):
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

    def create_random_shapes(self):
        """ create a crop of each image in one of the random shapes() """

        for img_name in self.all_image_filenames:
            img = Image.open("{}{}".format(self.raw_img_path, img_name))
            # we want 400 px wide images in browser, 3 times that for retina
            if img.width >=  self.image_crop_size[0] and img.height >=  self.image_crop_size[1]:

                shape = self.random_shape(img)
                shape = (0,0,800,800)
                img.crop(shape).save("{}{}".format(self.img_path, img_name))

            else:
                print("{} too small at {}x{}".format(img_name, str(img.width), str(img.height) ))

    def random_shape(self, img):
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

    def render_html(self):
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


if __name__ == '__main__':
    fail_msg = """\n Please specify fetch or crop: \n
                      python images.py <fetch/crop/render/shape>
                      \n """
    try:
        action = sys.argv[1]
    except IndexError:
        print(fail_msg)
        sys.exit()

    image_maker = ImagePipeline();
    if  action == 'fetch':
        image_maker.fetch_images();
    elif action == 'crop':
        image_maker.create_thumbnails();
    elif action == 'render':
        image_maker.render_html();
    elif action == 'shapes':
        image_maker.create_random_shapes90;
    else:
        print(fail_msg)

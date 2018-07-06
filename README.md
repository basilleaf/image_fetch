# Image Fetch

For when you have a bunch of image urls in a json file and you want
to fetch them all and optionally make smaller sizes.

Command line python script fetches remote images from a list of links
from json file, make thumbnails and a few other crop shapes,
and a utility to render an html list of these images to stdout.

## How To

- Edit config.py

- Customize the method read_json_file() in images.py to read your json file.

- run:


        python images.py <fetch/crop/render/shape>


A sample data.son is included in this repo

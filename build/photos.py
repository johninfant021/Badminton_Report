"""Player photos: crops each picture in ../Profile around the face and returns small JPEG data URIs.

FACE gives, per player, the face centre (fx, fy as fractions of image width/height) and the
face height (fh, fraction of image height). Adjust these if a new photo is added.
"""
import base64, io, os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'Profile')
FILES = {'Anto': 'Anto.png', 'Jothi Sai': 'sai.jpeg', 'John': 'John.jpg', 'Pawan': 'Pawan.jpg',
         'Dinesh': 'Dinesh.jpeg', 'Pratap': 'Prathap.png', 'Bhanu': 'Bhanu.png'}
FACE = {'Anto': (0.50, 0.32, 0.25), 'Jothi Sai': (0.51, 0.27, 0.17), 'John': (0.53, 0.33, 0.16),
        'Pawan': (0.415, 0.355, 0.095), 'Dinesh': (0.53, 0.25, 0.18), 'Pratap': (0.54, 0.20, 0.20),
        'Bhanu': (0.52, 0.17, 0.11)}


def _load(p):
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, FILES[p])))
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (20, 24, 36)); bg.paste(im, mask=im.split()[-1]); im = bg
    return im.convert('RGB')


def _crop(im, cx, cy, w, h):
    """Crop a w x h box centred on (cx, cy), shifted to stay inside the image and shrunk if it cannot fit."""
    s = min(1.0, im.width / w, im.height / h)
    w, h = w * s, h * s
    x0 = min(max(cx - w / 2, 0), im.width - w); y0 = min(max(cy - h / 2, 0), im.height - h)
    return im.crop((round(x0), round(y0), round(x0 + w), round(y0 + h)))


def crops(p):
    im = _load(p); fx, fy, fh = FACE[p]
    cx, cy, f = fx * im.width, fy * im.height, fh * im.height
    avatar = _crop(im, cx, cy + 0.12 * f, 2.5 * f, 2.5 * f).resize((240, 240), Image.LANCZOS)
    ph = 4.4 * f  # head and shoulders, 4:5
    portrait = _crop(im, cx, cy - 1.0 * f + ph / 2, ph * 0.8, ph).resize((480, 600), Image.LANCZOS)
    return avatar, portrait


def data_uri(img, q=80):
    b = io.BytesIO(); img.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def all_photos():
    out = {}
    for p in FILES:
        a, pt = crops(p)
        out[p] = dict(avatar=data_uri(a, 82), portrait=data_uri(pt, 78))
    return out


if __name__ == '__main__':
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_photo_check.jpg')
    tiles = [crops(p) for p in FILES]
    sheet = Image.new('RGB', (7 * 250, 250 + 610), 'white')
    for i, (a, pt) in enumerate(tiles):
        sheet.paste(a, (i * 250, 0)); sheet.paste(pt.resize((240, 300)), (i * 250, 250))
    sheet.save(dest, quality=85)
    print(dest, {p: (len(v['avatar']) + len(v['portrait'])) // 1024 for p, v in all_photos().items()}, 'KB')

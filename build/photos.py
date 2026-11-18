"""Player photos from ../Profile.

portrait: a 3:4 head-and-shoulders frame cut around the face, so every player is framed the same way:
          the face box fills about PORTRAIT_FACE of the width with its centre PORTRAIT_EYE of the way down.
          A photo too tight to allow that is used whole; only a photo smaller than the frame in both
          directions is padded with a blurred, darkened copy of itself.
avatar:   a square around the face for the small round pictures, face centre slightly above the middle.
FACE_OVERRIDE holds the face box (centre x, centre y, width, as fractions of the photo) measured with
OpenCV's frontal-face Haar cascade (opencv-python-headless < 5); Pawan looks up mid-smash, which the
cascade misses, so that one is measured by hand. A new photo needs its entry updated (or removed, to
let detection run).

To add or swap a photo: put it in ../Profile with the player's file name (any of .png .jpg .jpeg .webp).
"""
import base64, io, os, glob
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'Profile')
# file name without extension: the first image in Profile/ with this name is used
FILES = {'Anto': 'Anto', 'Jothi Sai': 'sai', 'John': 'John', 'Pawan': 'Pawan', 'Dinesh': 'Dinesh', 'Pratap': 'Prathap', 'Bhanu': 'Bhanu'}
# face box: centre x, centre y (fractions of width/height) and box width (fraction of width)
FACE_OVERRIDE = {'Anto': (0.485, 0.232, 0.321), 'Jothi Sai': (0.512, 0.270, 0.197), 'John': (0.477, 0.279, 0.222),
                 'Pawan': (0.410, 0.349, 0.160), 'Dinesh': (0.566, 0.237, 0.198), 'Pratap': (0.505, 0.368, 0.412),
                 'Bhanu': (0.520, 0.171, 0.196)}
PORTRAIT_FACE = 0.30   # face box width / frame width
PORTRAIT_EYE = 0.33    # face centre height / frame height
AVATAR_SIDE = 2.3      # avatar side / face box width
RATIO = 3 / 4
PW, PH = 540, 720


def _path(p):
    stem = FILES[p].lower()
    for f in sorted(glob.glob(os.path.join(SRC, '*'))):
        if os.path.splitext(os.path.basename(f))[0].lower() == stem and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            return f
    raise FileNotFoundError(f'No photo for {p} in Profile/ (looked for {FILES[p]}.png/.jpg/.jpeg/.webp)')


def _load(p):
    im = ImageOps.exif_transpose(Image.open(_path(p)))
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (12, 16, 24)); bg.paste(im, mask=im.split()[-1]); im = bg
    return im.convert('RGB')


def _detect(im):
    """Largest face in the upper part of the picture: (cx, cy, w) in pixels, or None."""
    try:
        import cv2, numpy as np
    except ImportError:
        return None
    g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    sc = min(1.0, 900 / max(g.shape))
    if sc < 1:
        g = cv2.resize(g, None, fx=sc, fy=sc)
    g = cv2.equalizeHist(g)
    for casc in ('haarcascade_frontalface_default.xml', 'haarcascade_frontalface_alt2.xml', 'haarcascade_profileface.xml'):
        try:
            det = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, casc))
        except AttributeError:  # OpenCV 5 no longer ships the Haar face models
            return None
        for flip in (False, True):
            gg = cv2.flip(g, 1) if flip else g
            faces = det.detectMultiScale(gg, scaleFactor=1.06, minNeighbors=6, minSize=(int(g.shape[1] * .06),) * 2)
            faces = [f for f in faces if f[1] + f[3] / 2 < g.shape[0] * 0.65]
            if len(faces):
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                if flip:
                    x = g.shape[1] - x - w
                return (x + w / 2) / sc, (y + h / 2) / sc, w / sc
    return None


def face(p, im):
    if p in FACE_OVERRIDE:
        fx, fy, fw = FACE_OVERRIDE[p]
        return fx * im.width, fy * im.height, fw * im.width, 'manual'
    d = _detect(im)
    if d:
        return d[0], d[1], d[2], 'detected'
    return im.width / 2, im.height * 0.28, im.width * 0.22, 'default'


def _square(im, cx, cy, side):
    side = min(side, im.width, im.height)
    x0 = min(max(cx - side / 2, 0), im.width - side); y0 = min(max(cy - side / 2, 0), im.height - side)
    return im.crop((round(x0), round(y0), round(x0 + side), round(y0 + side)))


def portrait(im, cx=None, cy=None, fw=None):
    """3:4 head-and-shoulders frame around the face (see the module note)."""
    if cx is not None:
        w = fw / PORTRAIT_FACE; h = w / RATIO
        # never ask for more than the photo has: shrink the frame (keeping 3:4) until it fits
        k = min(1.0, im.width / w, im.height / h); w *= k; h *= k
        x0 = min(max(cx - w / 2, 0), im.width - w); y0 = min(max(cy - PORTRAIT_EYE * h, 0), im.height - h)
        return im.crop((round(x0), round(y0), round(x0 + w), round(y0 + h))).resize((PW, PH), Image.LANCZOS)
    if abs(im.width / im.height - RATIO) < 0.012:
        return im.resize((PW, PH), Image.LANCZOS)
    bg = ImageOps.fit(im, (PW, PH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = im.copy(); fg.thumbnail((PW, PH), Image.LANCZOS)
    bg.paste(fg, ((PW - fg.width) // 2, (PH - fg.height) // 2))
    return bg


def crops(p):
    im = _load(p)
    cx, cy, fw, how = face(p, im)
    # the box is roughly brow to chin: widen it to take in hair, ears and a little of the shoulders,
    # with the face centre just above the middle of the square
    side = AVATAR_SIDE * fw
    avatar = _square(im, cx, cy + 0.06 * side, side).resize((240, 240), Image.LANCZOS)
    return avatar, portrait(im, cx, cy, fw), how


def data_uri(img, q=80):
    b = io.BytesIO(); img.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def all_photos():
    out = {}
    for p in FILES:
        a, pt, how = crops(p)
        out[p] = dict(avatar=data_uri(a, 84), portrait=data_uri(pt, 80), face=how)
    return out


if __name__ == '__main__':
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '_photo_check.jpg')
    sheet = Image.new('RGB', (7 * 250, 250 + 330), 'white')
    for i, p in enumerate(FILES):
        a, pt, how = crops(p)
        sheet.paste(a, (i * 250, 0)); sheet.paste(pt.resize((240, 320)), (i * 250, 255))
        print(p, os.path.basename(_path(p)), how)
    sheet.save(dest, quality=85)
    print(dest)

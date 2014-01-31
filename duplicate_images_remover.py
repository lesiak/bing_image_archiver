from PIL import Image
from functools import reduce

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 64
    return reduce(lambda x, y_z: x | (y_z[1] << y_z[0]),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)


def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h


if __name__ == '__main__':

    img1 = "D:/GIT/bing_image_downloader/Duplicate_tests/2013-12-03_ROW12447501718_Emperor-penguin-chicks-on-Snow-Hill-Island-Antarctica.jpg"
    img2 = "D:/GIT/bing_image_downloader/Duplicate_tests/2013-12-15_ZH-CN10127540833_E68CAAE5A881E88AACE9A9ACE5858BEFBC8CE58DA1E68B89E7B4A2E5858BE99984E8BF91E69D91E890BDE9878CE79A84E9A9AFE9B9BF.jpg"

    hash1 = avhash(img1)
    hash2 = avhash(img2)
    dist = hamming(hash1, hash2)
    print("hash(%s) = %d\nhash(%s) = %d\nhamming distance = %d\nsimilarity = %d%%" % (img1, hash1, img2, hash2, dist, (64 - dist) * 100 / 64))
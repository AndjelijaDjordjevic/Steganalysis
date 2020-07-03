import sys
import struct
import numpy
import matplotlib.pyplot as plt
from PIL import Image
from Crypto.Cipher import AES


def decompose(data):

    x = []
    size = len(data)
    bytes = [b for b in struct.pack("i", size)]
    bytes += [b for b in data]
    for b in bytes:
        for i in range(7, -1, -1):
            x.append((b >> i) & 0x1)
    return x


def set_bit(n, i, x):
    mask = 1 << i
    n &= ~mask
    if x:
        n |= mask
    return n


def embedding(imageFile, messageFile):
    img = Image.open(imageFile)
    (width, height) = img.size
    conv = img.convert("RGBA").getdata()
    max_size = width * height * 3.0 / 8 / 1024
    print("Maximum message size: %.2f KB." % (max_size))

    f = open(messageFile, "rb")
    data = f.read()
    f.close()

    password = b'Sixteen byte key'
    cipher = AES.new(password, AES.MODE_EAX)
    data_enc = cipher.encrypt(data)

    x = decompose(data_enc)

    while (len(x) % 3):
        x.append(0)

    message_size = len(x) / 8 / 1024.0
    if (message_size > max_size - 4):
        print("Cannot embed. File too large")
        sys.exit()

    steg_img = Image.new('RGBA', (width, height))
    data_img = steg_img.getdata()

    idx = 0

    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            if idx < len(x):
                r = set_bit(r, 0, x[idx])
                g = set_bit(g, 0, x[idx + 1])
                b = set_bit(b, 0, x[idx + 2])
            data_img.putpixel((w, h), (r, g, b, a))
            idx = idx + 3

    steg_img.save(imageFile + "-stego.png", "PNG")

    print("Embedding finished successfully!")


def analyse(in_file):

    BS = 100
    img = Image.open(in_file)
    (width, height) = img.size
    conv = img.convert("RGBA").getdata()

    red = []
    green = []
    blue = []
    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            red.append(r & 1)
            green.append(g & 1)
            blue.append(b & 1)

    averageRed = []
    averageGreen = []
    averageBlue = []
    for i in range(0, len(red), BS):
        averageRed.append(numpy.mean(red[i:i + BS]))
        averageGreen.append(numpy.mean(green[i:i + BS]))
        averageBlue.append(numpy.mean(blue[i:i + BS]))

    numBlocks = len(averageRed)
    blocks = [i for i in range(0, numBlocks)]
    plt.axis([0, len(averageRed), 0, 1])
    plt.ylabel('Average LSB per block')
    plt.xlabel('Block number')

    plt.plot(blocks, averageBlue, 'bo')

    plt.show()


if __name__ == "__main__":

    if sys.argv[1] == "hide":
        embedding(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "analyse":
        analyse(sys.argv[2])

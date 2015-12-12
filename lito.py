"""A simple litophany generator

"""

import sys, os, codecs
from PIL import Image
from PIL import ImageFilter

class heightmap(object):

    def __init__(self, img, xyscale = 1.0, zscale = 100.0):
        self.img = img.convert(mode="L")
        self.xyscale = xyscale
        self.zscale = zscale
        self.faces = []
        self.vertices = []
        self.addVertices()
        
    def addVertices(self):
        pixels = self.img.load()
        w,h = self.img.size
        for y in range(h):
            for x in range(w):
                xf = float(x) * self.xyscale
                yf = float(y) * self.xyscale
                val = pixels[x,y]
                zf = float(val)/255.0 * self.zscale
                self.vertices.append( (xf,yf,zf) )
    
    def triangulate(self):
        w,h = self.img.size
        for y in range(1, h):
            for x in range(1, w):
                prev_x  = (x-1) + y     * w
                prev_y  =     x + (y-1) * w
                prev_xy = (x-1) + (y-1) * w
                cur     =     x + y     * w
                self.addFace(prev_xy, prev_y, cur)
                self.addFace(prev_xy, cur, prev_x)

    def addFace(self, v1, v2, v3):
        """add one for objs sake"""
        self.faces.append ( (v1+1, v2+1, v3+1) )

    def store(self, fn):
        with codecs.open(fn, 'w', 'utf-8') as out:
            for v in self.vertices:
                out.write("v {} {} {}\n".format(*v))
            out.write("\n")
            for f in self.faces:
                out.write("f {} {} {}\n".format(*f))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(-1)
        

    fn = sys.argv[1]
    
    img = Image.open(fn).filter(ImageFilter.EDGE_ENHANCE).filter(ImageFilter.MedianFilter(5))
    #.filter(ImageFilter.GaussianBlur())

    img.show()

    hm = heightmap(img)
    hm.triangulate()
    hm.store("lito.obj")

    input("Await keypress...")

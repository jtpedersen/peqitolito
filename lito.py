"""A simple litophany generator

"""

import sys, os, codecs
from PIL import Image
from PIL import ImageFilter

class heightmap(object):

    def __init__(self, img, xyscale = 1.0, zscale = 100.0, zoffset = 10.0):
        self.img = img.convert(mode="L")
        self.xyscale = xyscale
        self.zscale = zscale
        self.zoffset = zoffset
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
                zf = float(val)/255.0 * self.zscale + self.zoffset
                self.addVertex( (xf,yf,zf) )
    
    def addVertex(self, v):
        self.vertices.append(v)

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


    def boxify(self):
        """turn into a box

        for each outer edge create lower version at (x,y,0)
        and add a quad if possible
        # TODO: this does create a few duplicate vertices, 
        """
        w,h = self.img.size
        self.addSkirt( [ i for i in range(w)])
        self.addSkirt( [ i + w*(h-1) for i in range(w)])
        self.addSkirt( [ j*w for j in range(h)], stride = w)
        self.addSkirt( [ j*w + w-1 for j in range(h)], stride = w)

        self.addBottom()
            
    def addSkirt(self, top_indicies, stride = 1):
        for i in range(len(top_indicies)):
            idx = top_indicies[i]
            x,y,z =  self.vertices[idx] 
            self.addVertex(  (x,y, 0) )
            if i > 0:
                self.addBackQuad(idx, stride)

    def addBackQuad(self, top, stride):
        """ given to indices above eachother 
        create a quad 
        the last index is the last in the list of vertices
        """
        bottom = len(self.vertices)-1
        self.addFace(top, top-stride, bottom)
        self.addFace(top-stride, bottom-1, bottom)
        
    def addBottom(self):
        w,h = self.img.size
        self.addVertex( (w/2, h/2, 0) )
        c = len(self.vertices)-1
        for idx in range(w*h, c):
            self.addFace(idx, idx -1, c)

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
    hm.boxify()
    hm.store("lito.obj")

    input("Await keypress...")

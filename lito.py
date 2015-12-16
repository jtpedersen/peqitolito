#!/usr/bin/env python3
"""A simple litophany generator

Usage: 
  lito [options] <image> <outfile>

Options:
  -d --dimension=DIMENSION  Maximal dimension [default: 10.0] 
  -z --zoffset=ZOFFSET      Padding in bottom to avoid holes [default: 0.3]
  -s --zscale=ZSCALE        Maximal height in [default: 2.5]
  -h  -help                 This screen
  -v --version              Version informaion

"""

import sys, os, codecs
from PIL import Image
from PIL import ImageFilter
from docopt import docopt
import pprint 
pp = pprint.PrettyPrinter(indent=4)


class heightmap(object):

    def __init__(self, img, xyscale, zscale, zoffset):
        self.img = img.convert(mode="L")
        self.xyscale = xyscale
        self.zscale = zscale / 255.0
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
                yf = float(h - y - 1) * self.xyscale
                val = float(255 - pixels[x,y])
                zf = val * self.zscale
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
            self.addVertex(  (x,y, -self.zoffset) )
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
        self.addVertex( (self.xyscale * w/2, self.xyscale * h/2, -self.zoffset) )
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
    args = docopt(__doc__, version = "PeqitoLito 0.1b")
    pp.pprint(args)

    fn = args['<image>']
    dim = float(args['--dimension'])
    zoffset = float(args['--zoffset'])
    zscale = float(args['--zscale'])
    outfile = args['<outfile>']
    img = Image.open(fn)
    #.filter(ImageFilter.EDGE_ENHANCE).filter(ImageFilter.MedianFilter(5))
    #.filter(ImageFilter.GaussianBlur())

#    img.show()
    xyscale = dim / float(max(*img.size))
    print("image : {}x{}".format(*img.size))
    print("Scaling xy:{} z:{} ".format(xyscale, zscale))
    hm = heightmap(img, xyscale = xyscale, zoffset = zoffset , zscale = zscale)
    hm.triangulate()
    hm.boxify()
    hm.store(outfile)

 #   input("Await keypress...")

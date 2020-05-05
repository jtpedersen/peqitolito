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
from skimage import io, transform
import numpy

from docopt import docopt
import pprint
pp = pprint.PrettyPrinter(indent=4)


class heightmap(object):

    def __init__(self, img,  z_max, zoffset):
        self.img = img
        self.zoffset = zoffset
        self.z_max = z_max
        self.faces = []
        self.vertices = []
        self.max_h = 0
        self.addVertices()


    def addVertices(self):
        w,h = self.img.shape
        for y in range(h):
            for x in range(w):
                xf = float(x)
                yf = float(y)
                self.addVertex( (xf,yf,self.img[x][y]) )

    def addVertex(self, v):
        self.max_h = max(self.max_h, v[2])
        self.vertices.append(v)

    def triangulate(self):
        w,h = self.img.shape
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
        w,h = self.img.shape
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
        w,h = self.img.shape
        self.addVertex( ( w/2,  h/2, -self.zoffset) )
        c = len(self.vertices)-1
        for idx in range(w*h, c):
            self.addFace(idx, idx -1, c)

    def store(self, fn):
        with codecs.open(fn, 'w', 'utf-8') as out:
            for v in self.vertices:
                out.write("v {} {} {}\n".format(v[0], v[1], self.z_max * v[2] / self.max_h))
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
    img = io.imread(fn, as_gray = True)

    xyscale = dim / float(max(img.shape))
    print("image : {}x{}".format(*img.shape))
    print("Scaling xy:{} z:{} ".format(xyscale, zscale))
    img = transform.rescale(img, xyscale, anti_aliasing = True)
    hm = heightmap( img, zoffset = zoffset , z_max = zscale)
    hm.triangulate()
    hm.boxify()
    hm.store(outfile)

 #   input("Await keypress...")

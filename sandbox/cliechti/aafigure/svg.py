"""
SVG renderer.

(C) 2006 Chris Liechti <cliechti@gmx.net>
"""

from xml.sax.saxutils import escape

class SVGOutputVisitor:
    """Render a list of shapes as ASCII art.
    """
    
    def __init__(self, file_like, scale = 1, line_width=1, unit='px', debug=False):
        self.file_like = file_like
        self.scale = scale
        self.unit = unit
        self.debug = debug
        self.line_width = line_width
    
    def _num(self, number):
        """helper to format numbers with scale and unit for svg output"""
        return "%d%s" % (number*self.scale, self.unit)

    def _unit(self, number):
        """helper to format numbers with unit for svg output"""
        return "%d%s" % (number, self.unit)

    def get_size_attrs(self):
        """get image size as svg text"""
        #this function is here beacuse of a hack. the rst2html converter
        #has to know the size of the figure it inserts
        return 'width="%s" height="%s"' % (
            self._num(self.width),
            self._num(self.height)
        )
    
    def visit(self, aa_image):
        """Process the gived ASCIIArtFigure and output the shapes in
           the SVG file
        """
        self.aa_image = aa_image        #save fore later XXX not optimal to do it here
        self.width = (aa_image.width+1)*aa_image.nominal_size
        self.height = (aa_image.height+1)*aa_image.nominal_size
        self.file_like.write("""\
<?xml version="1.0" standalone="no" ?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
  "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg width="%s" height="%s" xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink">
""" % (
            self._num(self.width),
            self._num(self.height)
        ))
  
        #~ if self.debug:
            #~ #draw a rectangle around entire image
            #~ self._rectangle(
                #~ 0,0,
                #~ aa_image.width, aa_image.height,
                #~ style = 'fill:none;',
            #~ )
        
        for shape in aa_image.shapes:
            shape_name = shape.__class__.__name__.lower()
            visitor_name = 'visit_%s' % shape_name
            if hasattr(self, visitor_name):
                getattr(self, visitor_name)(shape)
            else:
                print "WARNING: don't know how to handle shape %r" % shape
            
        self.file_like.write("""</svg>""")

    # - - - - - - SVG drawing helpers - - - - - - -
    def _line(self, x1, y1, x2, y2):
        """Draw a line, coordinates given as four decimal numbers"""
        self.file_like.write("""\
<line x1="%s" y1="%s" x2="%s" y2="%s"
    style="stroke:black; stroke-width:%s;" />
""" % (self._num(x1), self._num(y1), self._num(x2), self._num(y2), self._unit(self.line_width)))

    def _rectangle(self, x1, y1, x2, y2, style=''):
        """Draw a rectange, coordinates given as four decimal numbers.
           ``style`` is inserted in the SVG. It could be e.g. "fill:yellow"
        """
        self.file_like.write("""\
<rect x="%s" y="%s"
  width="%s"
  height="%s"
  style="stroke:black; stroke-width:%s; %s"
/>
""" % (
            self._num(x1), self._num(y1),
            self._num(x2-x1), self._num(y2-y1),
            self._unit(self.line_width),
            style
        ))

    # - - - - - - visitor function for the different shape types - - - - - - -
    
    def visit_point(self, point):
        self.file_like.write("""\
<circle cx="%s" cy="%s" r="%s" 
    style="fill:black; stroke:black; stroke-width:%s;" />
""" % (
        self._num(point.x), self._num(point.y),
        self._num(0.2),
        self._unit(self.line_width)))
    
    def visit_line(self, line):
        self.file_like.write("<!-- line -->\n")
        x1, x2 = line.start.x, line.end.x
        y1, y2 = line.start.y, line.end.y
        self._line(x1, y1, x2, y2)
    
    def visit_rectangle(self, rectangle):
        self._rectangle(
            rectangle.p1.x, rectangle.p1.y,
            rectangle.p2.x, rectangle.p2.y
        )
        
    
    def visit_circle(self, circle):
        self.file_like.write("""\
<circle cx="%s" cy="%s" r="%s" 
    style="stroke:black; stroke-width:%s;" />
""" % (
        self._num(circle.center.x), self._num(circle.center.y),
        self._num(circle.radius),
        self._unit(self.line_width)))

    def visit_label(self, label):
        #  font-weight="bold"
        self.file_like.write("""\
<text x="%s" y="%s"
  font-family="Verdana,sans-serif"
  font-size="%s"
>
  %s
</text>
""" % (
        self._num(label.position.x), self._num(label.position.y-0.3), #XXX static offset not good in all situations
        self._num(self.aa_image.nominal_size),
        escape(label.text)
        ))

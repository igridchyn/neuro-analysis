#!/usr/bin/env python

from sys import argv
import numpy as np
from matplotlib import pyplot
import os
from iutils import *
from call_log import *

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

if len(argv) < 4:
	print 'USAGE: (1)<font path> (2)<image path> (3)<font size>'
	exit(0)

img = Image.open(argv[2])
draw = ImageDraw.Draw(img)
fs = int(argv[3])

# 1.03 normally; 1.05 y for some - raster ?
scale = 1.10
new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
new_im = Image.new("RGB", new_size, color=(255,255,255,0))
new_im.paste(img, (new_im.size[0] - img.size[0], new_im.size[1] - img.size[1]))
img = new_im
draw = ImageDraw.Draw(img)

#fonts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
#font = ImageFont.truetype(os.path.join(fonts_path, 'sans_serif.ttf'), 24)

#font = ImageFont.truetype("sans-serif.ttf", 16)
font = ImageFont.truetype(argv[1], fs) # 30
font15x = ImageFont.truetype(argv[1], int(fs*1.5)) # 30
fonttit = ImageFont.truetype(argv[1], 35) # 35
font_scale = ImageFont.truetype(argv[1], 25) # 35
# draw.text((x, y),"Sample Text",(r,g,b))

# raster - 1600 x 1120
#draw.text((5, 1),"A",(0,0,0),font=font)
#draw.text((800, 1),"B",(0,0,0),font=font)
#draw.text((5, 550),"C",(0,0,0),font=font)
#draw.text((800, 550),"D",(0,0,0),font=font)

# raster - 1560 x 1140
#draw.text((0, 0),"A",(0,0,0),font=font)
#draw.text((new_size[0]/2, 0),"B",(0,0,0),font=font)
#draw.text((0, new_size[1]/2 - 30),"C",(0,0,0),font=font)
#draw.text((new_size[0] / 2, new_size[1]/2 - 30),"D",(0,0,0),font=font)
# add lines - time calibration
#draw.line((700, 540, 760, 540), fill=(0,0,0,0), width = 3)
#draw.text((720, 540), "1 s", (0,0,0), font = font_scale)
# Y WAS 1150 
#draw.line((700, 1060, 780, 1060), fill=(0,0,0,0), width = 3)
#draw.text((720, 1060), "50 ms", (0,0,0), font = font_scale)

# BEH - LINES
#draw.text((250, 1),"A",(0,0,0),font=font)
#draw.text((900, 1),"B",(0,0,0),font=font)
#draw.text((1600, 1),"C",(0,0,0),font=font)

# BEH - 3 X 2 BARS; 1.1 X MAGN.
draw.text((200, 1),"A",(0,0,0),font=font)
draw.text((560, 1),"B",(0,0,0),font=font)
draw.text((960, 1),"C",(0,0,0),font=font)
img.show()

# BEH - SES WISE 1703 X 726
#draw.text((240, 1),"A",(0,0,0),font=font)
#draw.text((690, 1),"B",(0,0,0),font=font)
#draw.text((1130, 1),"C",(0,0,0),font=font)

# BEH SCORES - 3036 X 712
#draw.text((50, 1),"A",(0,0,0),font=font)
#draw.text((1080, 1),"B",(0,0,0),font=font)
#draw.text((2080, 1),"C",(0,0,0),font=font)

# PFS - 3X3 bars
#draw.text((10, 10),"A",(0,0,0),font=font)
#draw.text((822, 10),"B",(0,0,0),font=font)
#draw.text((1634, 10),"C",(0,0,0),font=font)

# WAKING COFIRINGS - POST AND POST-LEARNING
#draw.text((600, 50), "END OF LEARNING VS. POST-PROBE", (0,0,0), font=font)
#draw.text((30, 170),"A",(0,0,0),font=font15x)
#draw.text((770, 170),"B",(0,0,0),font=font15x)
#draw.text((1550, 170),"C",(0,0,0),font=font15x)
#draw.text((300, 1220), "END OF LEARNING VS. START OF POST-LEARNING", (0,0,0), font=font)
#draw.text((30, 1370),"D",(0,0,0),font=font15x)
#draw.text((770, 1370),"E",(0,0,0),font=font15x)
#draw.text((1550, 1370),"F",(0,0,0),font=font15x)

# PFS HISTS
#draw.text((90, 0),"A",(0,0,0),font=font)
#draw.text((1200, 0),"B",(0,0,0),font=font)
#draw.text((2350, 0),"C",(0,0,0),font=font)

# PHYS VS. BEH
#draw.text((60, 0),"A",(0,0,0),font=font)
#draw.text((1470, 0),"B",(0,0,0),font=font)
#draw.text((2870, 0),"C",(0,0,0),font=font)

# BARCOR VS. BEH 4236 X 1112
#draw.text((60, 0),"A",(0,0,0),font=font)
#draw.text((1470, 0),"B",(0,0,0),font=font)
#draw.text((2870, 0),"C",(0,0,0),font=font)


# FRS 3 X 3; 1236x2436
#draw.text((5, 20),"A",(0,0,0),font=font)
#draw.text((412, 20),"B",(0,0,0),font=font)
#draw.text((824, 20),"C",(0,0,0),font=font)
#draw.text((5, 822),"D",(0,0,0),font=font)
#draw.text((412, 822),"E",(0,0,0),font=font)
#draw.text((824, 822),"F",(0,0,0),font=font)
#draw.text((5, 1636),"G",(0,0,0),font=font)
#draw.text((412, 1636),"H",(0,0,0),font=font)
#draw.text((824, 1636),"I",(0,0,0),font=font)

#draw.text((480, 1),"Disrupted events",(0,0,0),font=fonttit)
#draw.text((450, 800),"Top 20% disrupted events",(0,0,0),font=fonttit)
#draw.text((500, 1620),"Control events",(0,0,0),font=fonttit)

# BS + 3 X 1
#draw.text((5, 1),"A",(0,0,0),font=font)
#draw.text((810, 1),"B",(0,0,0),font=font)
#draw.text((1620, 1),"C",(0,0,0),font=font)

# RESPONSES
#draw.text((60, 1),"A",(0,0,0),font=font)
#draw.text((1100, 1),"B",(0,0,0),font=font)
#draw.text((2070, 1),"C",(0,0,0),font=font)

#METHOD ACCURACY
#draw.text((0, 0),"A",(0,0,0),font=font)
#draw.text((911, 0),"B",(0,0,0),font=font)

# DECODING EXAMPLE TRAJECTORIES
#draw.text((0, 0),"A",(0,0,0),font=font)
#$draw.text((612, 0),"B",(0,0,0),font=font)

img.save(argv[2] + '.mod.png')

#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import random
import numpy as np 
import matplotlib.pyplot as plt

y=20
x=np.pi/2
w=np.pi/2

#yellow
color1 = '#fbbc05'
#blue
color2 = '#4285f4'
# red
color3 = '#ea4335'
#green 
color4 = '#34a853'

x1=[np.pi/10+np.pi*i/5 for i in range(1,11)]
x2=[np.pi/20+np.pi*i/5 for i in range(1,11)]
x3=[3*np.pi/20+np.pi*i/5 for i in range(1,11)]
y1=[7000 for i in range(0,10)]
y2=[6000 for i in range(0,10)]
#fig=plt.figure(figsize=(13.44,7.5))
fig=plt.figure(figsize=(2,2))
ax = fig.add_subplot(111,projection='polar')
ax.axis('off')

random.seed(200)
y4=[random.randint(4500,5700) for i in range(10)]
y5=[random.randint(3200,5000) for i in range(10)]

ax.bar(left=x2, height=y4,width=np.pi/10,color=color2,edgecolor=color2)
ax.bar(left=x3, height=y5,width=np.pi/10,color=color3,edgecolor=color3)

y6=[2000 for i in range(0,10)]
ax.bar(left=x1, height=y6,width=np.pi/5,color='w',edgecolor='w')

#plt.text(500, 500, 'Logan`s Blog', fontsize=40)

#fig.savefig('favicon.png',dpi=300,bbox_inches='tight',transparent=True)
fig.savefig('favicon.png',dpi=300,bbox_inches='tight',transparent=True)

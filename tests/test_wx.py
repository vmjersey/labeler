#!/usr/bin/env python3 

'''
This script is a very simple test of your wxpython installation
'''

import wx 

app = wx.App() 
window = wx.Frame(None, title = "wxPython Frame", size = (300,200)) 
panel = wx.Panel(window) 
label = wx.StaticText(panel, label = "Hello World", pos = (100,50)) 
window.Show(True) 

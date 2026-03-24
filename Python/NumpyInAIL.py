#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##########################################################################
#
# 
#  File name: NumpyInAIL.py  
#
#   Synopsis:  This example shows how to use Aurora Imaging Library in an Python project using numpy.
#
#  © 1992-2025 Zebra Technologies Corp. and/or its affiliates
#  All Rights Reserved
##########################################################################

import sys

try:
   import ail11 as AIL
except:
   print("Import Aurora Imaging Library failure.")
   print("An error occurred while trying to import ail11. Please make sure ail is under your python path.\n")
   print("Press any key to end.\n")
   input()
   sys.exit(2)

try:
   #All subsequent calls to Aurora Imaging Library that return an array will return a numpy array
   import numpy as np
except:
   print("Import numpy library failure.")
   print("An error occurred while trying to import numpy. Please make sure the numpy package is installed.\n")
   print("Press any key to end.\n")
   input()
   sys.exit(2)

try:
   #Lets plot the line data as a profile
   import sys
   if sys.platform == "linux" :
       import os
       import matplotlib
       if 'WAYLAND_DISPLAY' in os.environ:
          matplotlib.use('GTK3Agg')
       else:
          matplotlib.use('Qt5Agg')
   from matplotlib import pyplot as plt
except:
   print("Import matplotlib library failure.")
   print("An error occurred while trying to import matplotlib. Please make sure the matplotlib package is installed.\n")
   print("Press any key to end.\n")
   input()
   sys.exit(2)


def LineProfile(AilDisplay, GraphicsList, BaboonRGB):
   '''Create a line profile and display it in a chart'''
   print("Create a line profile and display it in a chart.")
   # Dimensions of line profile
   x_start = 135
   y_start = 135
   x_end = 365
   y_end = 315

   # Draw the line in the display
   AIL.MgraControl(AIL.M_DEFAULT, AIL.M_COLOR, AIL.M_COLOR_YELLOW)
   AIL.MgraLine(AIL.M_DEFAULT, GraphicsList, x_start, y_start, x_end, y_end)
   AIL.MdispControl(AilDisplay, AIL.M_ASSOCIATED_GRAPHIC_LIST_ID, GraphicsList)
   AIL.MdispSelect(AilDisplay, BaboonRGB)

   #Create child bands for each color
   red_band = AIL.MbufChildColor(BaboonRGB, AIL.M_RED)
   nb_pixels, red_line_data = AIL.MbufGetLine(red_band, x_start, y_start, x_end, y_end, AIL.M_DEFAULT)
   AIL.MbufFree(red_band)

   green_band = AIL.MbufChildColor(BaboonRGB, AIL.M_GREEN)
   nb_pixels, green_line_data = AIL.MbufGetLine(green_band, x_start, y_start, x_end, y_end, AIL.M_DEFAULT)
   AIL.MbufFree(green_band)

   blue_band = AIL.MbufChildColor(BaboonRGB, AIL.M_BLUE)
   nb_pixels, blue_line_data = AIL.MbufGetLine(blue_band, x_start, y_start, x_end, y_end, AIL.M_DEFAULT)
   AIL.MbufFree(blue_band)

   # Plot the lines using pyplot
   plt.plot(red_line_data, color='r', label='red band')
   plt.plot(green_line_data, color='g', label='green band')
   plt.plot(blue_line_data, color='b', label='blue band')
   plt.legend()
   plt.xlabel("Pixel Index")
   plt.ylabel("Pixel Value")
   plt.title("Line Profile of {0} Pixels".format(nb_pixels))
   plt.grid(True)
   print("Showing the data obtained from MbufGetLine (Line Profile)")
   print("Close the plot window to continue")
   plt.show()

   #Clean up
   AIL.MdispControl(AilDisplay, AIL.M_ASSOCIATED_GRAPHIC_LIST_ID, AIL.M_NULL)

def DisplayBuffer(BaboonRGB):
   '''Display a buffer using matplotlib by getting a copy of the buffer into a numpy array'''
   print("Display a buffer using matplotlib by getting a copy of the buffer into a numpy array")

   numpy_array = AIL.MbufGet(BaboonRGB) #Retrieves a planar buffer in (Band, SizeY, SizeX)
   
   #Rearrange the buffer to be packed to support imshow (SizeY, SizeX, Band)
   numpy_array = np.dstack((numpy_array[0], numpy_array[1], numpy_array[2]))
   plt.imshow(numpy_array)
   plt.xlabel("X")
   plt.ylabel("Y")
   plt.title("BaboonRGB {0}".format(numpy_array.shape))
   print("Showing the BaboonRBG buffer using pyplot")
   print("Close the plot window to continue")
   plt.show()

def CreateNumpyArrayFromAILBuffer(AilDisplay, AilSystem):
   '''Create a numpy array using the host address of a buffer'''
   print("Create a numpy array using the host address of a buffer")

   AIL.MsysControl(AilSystem, AIL.M_ALLOCATION_OVERSCAN, AIL.M_DISABLE) # Disable the overscan so we have a zero pitch
   
   # Create a numpy array using a monochrome buffer
   Image = AIL.MbufImport(AIL.M_IMAGE_PATH +"BaboonMono.mim", AIL.M_DEFAULT, AIL.M_RESTORE + AIL.M_NO_GRAB,  AilSystem)
   size_x = AIL.MbufInquire(Image, AIL.M_SIZE_X)
   size_y = AIL.MbufInquire(Image, AIL.M_SIZE_Y)
   pitch = AIL.MbufInquire(Image, AIL.M_PITCH)

   if pitch != size_x:
      print("There is padding on the buffer, which numpy does not support")
      sys.exit(2)

   import ctypes # We use ctypes to get the buffer address and provide it to numpy
   host_address = AIL.MbufInquire(Image, AIL.M_HOST_ADDRESS)
   host_address_ptr = ctypes.cast(host_address, ctypes.POINTER(ctypes.c_ubyte)) # Cast as a c_ubyte to match image format
   
   image_array = np.ctypeslib.as_array(host_address_ptr, (size_y, size_x)) # Create the numpy array from the address
   
   plt.imshow(image_array, cmap='gray') # Show that the array contains the same content
   print("Showing the BaboonMono buffer using pyplot")
   print("Close the plot window to continue")
   plt.show()

   AIL.MdispSelect(AilDisplay, Image) # Show the buffer before modification in AIL
   print("The image before modifying the numpy array")
   print("Press any key to continue")
   AIL.MosGetch()
   
   for x in range(0, image_array.shape[0]):
      for y in range(0, image_array.shape[1]):
         if image_array[x, y] > 128:
            image_array[x, y] = 128 # Saturate all pixel values to 128

   AIL.MbufControl(Image, AIL.M_MODIFIED, AIL.M_DEFAULT) # Indicate to Aurora Imaging Library the buffer has changed to trigger a display update
   print("The image after saturating the pixel values to 128 and signaling to Aurora Imaging Library the buffer has been modified")
   print("Press any key to continue")
   AIL.MosGetch()
   
   AIL.MbufFree(Image) # Once MbufFree is called the numpy array is no longer valid
   del image_array # Manually clear the numpy array to ensure no one tries to access it

   # Create a numpy array using an RGB buffer
   Image = AIL.MbufImport(AIL.M_IMAGE_PATH +"BaboonRGB.mim", AIL.M_DEFAULT, AIL.M_RESTORE + AIL.M_NO_GRAB,  AilSystem)
   size_x = AIL.MbufInquire(Image, AIL.M_SIZE_X)
   size_y = AIL.MbufInquire(Image, AIL.M_SIZE_Y)
   size_band = AIL.MbufInquire(Image, AIL.M_SIZE_BAND)
   data_format = AIL.MbufInquire(Image, AIL.M_DATA_FORMAT)
   pitch = AIL.MbufInquire(Image, AIL.M_PITCH)

   if pitch != size_x:
      print("There is padding on the buffer, which numpy does not support")
      sys.exit(2)

   import ctypes # We use ctypes to get the buffer address and provide it to numpy
   host_address = AIL.MbufInquire(Image, AIL.M_HOST_ADDRESS)
   host_address_ptr = ctypes.cast(host_address, ctypes.POINTER(ctypes.c_ubyte)) # Cast as a c_ubyte to match image format
   
   # Create the correct shape based on packed versus planar buffers
   if data_format & AIL.M_PACKED == AIL.M_PACKED:
      shape = (size_y, size_x, size_band)
   else:
      shape = (size_band, size_y, size_x)
   image_array = np.ctypeslib.as_array(host_address_ptr, shape) # Create the numpy array from the address in planar format

   AIL.MdispSelect(AilDisplay, Image) # Show the buffer before modification in AIL
   print("The image before modifying the numpy array")
   print("Press any key to continue")
   AIL.MosGetch()
   
   for y in range(0, image_array.shape[0]):
      for x in range(0, image_array.shape[1]):
         if image_array[y, x, 0] > 128:
            image_array[y, x, 0] = 128 # Saturate all pixel values to 128 in the first band

   AIL.MbufControl(Image, AIL.M_MODIFIED, AIL.M_DEFAULT) # Indicate to Aurora Imaging Library the buffer has changed to trigger a display update
   print("The image after saturating the first bands pixel values to 128 and signaling to Aurora Imaging Library the buffer has been modified")
   print("Press any key to continue")
   AIL.MosGetch()
   
   AIL.MbufFree(Image) # Once MbufFree is called the numpy array is no longer valid
   del image_array # Manually clear the numpy array to ensure no one tries to access it
   AIL.MsysControl(AilSystem, AIL.M_ALLOCATION_OVERSCAN, AIL.M_DEFAULT)

# MAIN 
def main():
   print("\n[SYNOPSIS]\n")
   print("This example shows how to use Aurora Imaging Library in an Python project using numpy.")
   
   AilApplication = AIL.MappAlloc("M_DEFAULT", AIL.M_DEFAULT)
   AilSystem = AIL.MsysAlloc(AilApplication, "M_DEFAULT", AIL.M_DEFAULT, AIL.M_DEFAULT)

      # First we check if the system is local
   if (AIL.MsysInquire(AilSystem, AIL.M_LOCATION) != AIL.M_LOCAL):
      print("\n\nThis example accesses the buffer host address which is not supported on a remote system.")
      print("Please select a local system as the default.")
      print("Press any key to end.\n")
      input()
   else:
      AilDisplay = AIL.MdispAlloc(AilSystem, AIL.M_DEFAULT, "M_DEFAULT", AIL.M_DEFAULT)
      GraphicsList = AIL.MgraAllocList(AilSystem, AIL.M_DEFAULT)
   
      BaboonRGB = AIL.MbufImport(AIL.M_IMAGE_PATH +"BaboonRGB.mim", AIL.M_DEFAULT, AIL.M_RESTORE + AIL.M_NO_GRAB,  AilSystem) #Restore an image
   
      '''Create a line profile and display it in a chart'''
      LineProfile(AilDisplay, GraphicsList, BaboonRGB)

      '''Display a buffer using matplotlib by getting a copy of the buffer into a numpy array'''
      DisplayBuffer(BaboonRGB)

      '''Create a numpy array using the host address of a buffer'''
      CreateNumpyArrayFromAILBuffer(AilDisplay, AilSystem)

      AIL.MbufFree(BaboonRGB)
      AIL.MdispFree(AilDisplay)
      AIL.MgraFree(GraphicsList)

   AIL.MsysFree(AilSystem)
   AIL.MappFree(AilApplication)

if __name__ == "__main__":
    main()

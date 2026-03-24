#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#################################################################################
#
#  File name: NumpyInAIL.py
#
#  Content:  This example shows how to use Aurora Imaging Library in an Python project using numpy.
#
#  © 1992-2025 Zebra Technologies Corp. and/or its affiliates
#  All Rights Reserved
#
##################################################################################

class IncorrectSetupException(Exception):
   pass

try:
   from ZebraAuroraImagingObjectLibrary11 import *
except:
   print("Import Aurora Imaging Library failure.")
   print("An error occurred while trying to import ail11. Please make sure ail is under your python path.")
   print("Press any key to end.")
   input()
   sys.exit(2)

try:
   #All subsequent calls to Aurora Imaging Library that return an array will return a numpy array
   import numpy as np
except:
   print("Import numpy library failure.")
   print("An error occurred while trying to import numpy. Please make sure the numpy package is installed.")
   print("Press any key to end.")
   input()
   sys.exit(2)

try:
   #Lets plot the line data as a profile
   import sys
   if sys.platform == "linux" :
       import matplotlib
       matplotlib.use('Qt5Agg')
   from matplotlib import pyplot as plt
except:
   print("Import matplotlib library failure.")
   print("An error occurred while trying to import matplotlib. Please make sure the matplotlib package is installed.")
   print("Press any key to end.")
   input()
   sys.exit(2)

class NumpyInAILExample(object):

   def LineProfile(self):
      '''Create a line profile and display it in a chart'''
      print("Create a line profile and display it in a chart.")
      # Dimensions of line profile
      x_start = 135
      y_start = 135
      x_end = 365
      y_end = 315

      # Draw the line in the display
      self._graphicContext.Color = Color8.Yellow
      self._graphicContext.DrawLine(self._graList, x_start, y_start, x_end, y_end)
      self._display.AssociatedGraphicList = self._graList
      self._display.Select(self._image)

      #Create child bands for each color
      red_band = self._image.ChildColor(Buf.ColorBand.Red)
      nb_pixels, red_line_data = red_band.GetLine(x_start, y_start, x_end, y_end)
      red_band.Free() if red_band is not None else None

      green_band = self._image.ChildColor(Buf.ColorBand.Green)
      nb_pixels, green_line_data = green_band.GetLine(x_start, y_start, x_end, y_end)
      green_band.Free() if green_band is not None else None

      blue_band = self._image.ChildColor(Buf.ColorBand.Blue)
      nb_pixels, blue_line_data = blue_band.GetLine(x_start, y_start, x_end, y_end)
      blue_band.Free() if blue_band is not None else None

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
      self._display.AssociatedGraphicList = Gra.List()

   def DisplayBuffer(self):
      '''Display a buffer using matplotlib by getting a copy of the buffer into a numpy array'''
      print("Display a buffer using matplotlib by getting a copy of the buffer into a numpy array")

      numpy_array = self._image.Get(None)

      #Rearrange the buffer to be packed to support imshow (SizeY, SizeX, Band)
      numpy_array = np.dstack((numpy_array[0], numpy_array[1], numpy_array[2]))
      plt.imshow(numpy_array)
      plt.xlabel("X")
      plt.ylabel("Y")
      plt.title("BaboonRGB {0}".format(numpy_array.shape))
      print("Showing the BaboonRBG buffer using pyplot")
      print("Close the plot window to continue")
      plt.show()

   def CreateNumpyArrayFromAILBuffer(self):
      '''Create a numpy array using the host address of a buffer'''
      print("Create a numpy array using the host address of a buffer")

      self._system.AllocationOverscan = Sys.AllocationOverscan.Disable # Disable the overscan so we have a zero pitch

      # Create a numpy array using a monochrome buffer
      image = Buf.Image(Paths.Images + "BaboonMono.mim", self._system)
      size_x = image.SizeX
      size_y = image.SizeY
      pitch = image.Pitch

      if pitch != size_x:
         image.Free() if image is not None else None
         raise IncorrectSetupException("There is padding on the buffer, which numpy does not support.")

      import ctypes # We use ctypes to get the buffer address and provide it to numpy
      host_address = image.HostAddress
      host_address_ptr = ctypes.cast(host_address, ctypes.POINTER(ctypes.c_ubyte)) # Cast as a c_ubyte to match image format

      image_array = np.ctypeslib.as_array(host_address_ptr, (size_y, size_x)) # Create the numpy array from the address

      plt.imshow(image_array, cmap='gray') # Show that the array contains the same content
      print("Showing the BaboonMono buffer using pyplot")
      print("Close the plot window to continue")
      plt.show()

      self._display.Select(image) # Show the buffer before modification in AIL
      print("The image before modifying the numpy array")
      print("Press any key to continue")
      Os.Getch()

      for x in range(0, image_array.shape[0]):
         for y in range(0, image_array.shape[1]):
            if image_array[x, y] > 128:
               image_array[x, y] = 128 # Saturate all pixel values to 128

      image.Modified() # Indicate to Aurora Imaging Library the buffer has changed to trigger a display update
      print("The image after saturating the pixel values to 128 and signaling to Aurora Imaging Library the buffer has been modified")
      print("Press any key to continue")
      Os.Getch()

      image.Free() if image is not None else None # Once MbufFree is called the numpy array is no longer valid
      del image_array # Manually clear the numpy array to ensure no one tries to access it

      # Create a numpy array using an RGB buffer
      image = Buf.Image()
      image.Restore(Paths.Images + "BaboonRGB.mim", self._system, Buf.ImageRestoreOptions.NoGrab)
      size_x = image.SizeX
      size_y = image.SizeY
      pitch = image.Pitch
      size_band = image.SizeBand
      data_format = image.DataFormat

      if pitch != size_x:
         image.Free() if image is not None else None
         raise IncorrectSetupException("There is padding on the buffer, which numpy does not support.")

      import ctypes # We use ctypes to get the buffer address and provide it to numpy
      host_address = image.HostAddress
      host_address_ptr = ctypes.cast(host_address, ctypes.POINTER(ctypes.c_ubyte)) # Cast as a c_ubyte to match image format

      # Create the correct shape based on packed versus planar buffers
      if data_format & Buf.DataFormats.Packed == Buf.DataFormats.Packed:
         shape = (size_y, size_x, size_band)
      else:
         shape = (size_band, size_y, size_x)
      image_array = np.ctypeslib.as_array(host_address_ptr, shape) # Create the numpy array from the address in planar format

      self._display.Select(image) # Show the buffer before modification in AIL
      print("The image before modifying the numpy array")
      print("Press any key to continue")
      Os.Getch()

      for y in range(0, image_array.shape[0]):
         for x in range(0, image_array.shape[1]):
            if image_array[y, x, 0] > 128:
               image_array[y, x, 0] = 128 # Saturate all pixel values to 128 in the first band

      image.Modified() # Indicate to Aurora Imaging Library the buffer has changed to trigger a display update
      print("The image after saturating the first bands pixel values to 128 and signaling to Aurora Imaging Library the buffer has been modified")
      print("Press any key to continue")
      Os.Getch()

      image.Free() if image is not None else None # Once MbufFree is called the numpy array is no longer valid
      del image_array # Manually clear the numpy array to ensure no one tries to access it
      self._system.AllocationOverscan = Sys.AllocationOverscan.Enable

   def __init__(self):
      self._application = App.Application(App.AllocInitFlags.Default)
      self._system = Sys.System(self._application)

      # First we check if the system is local
      if (self._system.Location != Sys.Location.Local):
         print("\nThis example accesses the buffer host address which is not supported on a remote system.")
         print("Please select a local system as the default.")
         print("Press any key to end.\n")
         input()
         sys.exit(2)

      else:
         self._graList = Gra.List(self._system)
         self._display = Disp.Display(self._system)
         self._graphicContext = Gra.Context(self._system)
         self._image = 0

   def __enter__(self):
      return self

   def Run(self):
      print("\n[SYNOPSIS]\n")
      print("This example shows how to use Aurora Imaging Library in an Python project using numpy.")

      self._image = Buf.Image(Paths.Images + "BaboonRGB.mim", self._system)

      '''Create a line profile and display it in a chart'''
      self.LineProfile()

      '''Display a buffer using matplotlib by getting a copy of the buffer into a numpy array'''
      self.DisplayBuffer()

      '''Create a numpy array using the host address of a buffer'''
      self.CreateNumpyArrayFromAILBuffer()

   def __exit__(self, exc_type, exc_value, tb):
      self._image.Free() if self._image is not None else None
      self._graList.Free() if self._graList is not None else None
      self._display.Free() if self._display is not None else None
      self._graphicContext.Free() if self._graphicContext is not None else None
      self._system.Free() if self._system is not None else None
      self._application.Free() if self._application is not None else None

if __name__ == "__main__":
   try:
      with NumpyInAILExample() as example:
         example.Run()
   except IncorrectSetupException as exception:
      print(exception)
      print("Press any key to exit.")
      Os.Getch()
   except AIOLException as exception:
      print("Encountered an exception during the example.")
      print(exception)
      print("Press any key to exit.")
      Os.Getch()

#!/usr/bin/env python
#Copyright 2005 Sebastian Hagen
# This file is part of alfredi.

# alfredi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# alfredi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with alfredi; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

class PointByCoordinates:
   def __init__(self, latitude, longitude):
      if not (-90 <= latitude <= 90):
         raise ValueError('Invalid value %r for latitude.' % (latitude,))
      if not (-180 <= longitude <= 180):
         raise ValueError('Invalid value %r for longitude.' % (longitude,))
      self.latitude = float(latitude)
      self.longitude = float(longitude)
      
   def __repr__(self):
      return '%s(latitude=%f, longitude=%f)' % (self.__class__.__name__, self.latitude, self.longitude)
   
   def fromhybrid(object_class, latitude_hybrid, longitude_hybrid):
      results = []
      for data_tuple in (latitude_hybrid, longitude_hybrid):
         (degrees, minutes, seconds) = data_tuple
         if not (0 <= minutes < 60):
            raise ValueError('%f is an invalid value for degree minutes.' % minutes)
         if not (0 <= seconds < 60):
            raise ValueError('%f is an invalid value for degreee seconds.' % seconds)
         
         results.append(degrees + minutes/60.0 + seconds/3600.0)
      
      return object_class(*results)
      
   fromhybrid = classmethod(fromhybrid)
      
   def __eq__(self, other):
      if (isinstance(other, self.__class__) and (self.latitude == other.latitude) and (self.longitude == other.longitude)):
         return True
      return False
   def __ne__(self, other):
      return (not (self == other))
   
   def __add__(self, other):
      if not (isinstance(other, self.__class__)):
         raise TypeError("Can't add object %r to myself %r of class %r." % (other, self, self.__class__))
      return self.__class__(self.latitude+other.latitude, self.longitude+other.longitude)
   
   def __sub__(self,other):
      if not (isinstance(other, self.__class__)):
         raise TypeError("Can't subtract object %r from myself %r of class %r." % (other, self, self.__class__))
      return DeltaByCoordinates(self.latitude-other.latitude, self.longitude-other.longitude)


class DeltaByCoordinates(PointByCoordinates):
   def __init__(self, latitude, longitude):
      if not (-180 <= latitude <= 180):
         raise ValueError('Invalid value %r for latitude.' % (latitude,))
      if not (-360 <= longitude <= 360):
         raise ValueError('Invalid value %r for longitude.' % (longitude,))
      self.latitude = float(latitude)
      self.longitude = float(longitude)


class CoordsToOffsetConverter:
   def __init__(self, coord_zero, coord_one, length_x, length_y):
      self.coord_zero = coord_zero
      self.coord_one = coord_one
      self.coord_delta = coord_delta = coord_one - coord_zero
      self.length_x = length_x
      self.height_y = length_y
      self.factor_x = length_x/float(coord_delta.longitude)
      self.factor_y = length_y/float(coord_delta.latitude)

   def __call__(self, coord, sanity=True):
      if (sanity):
         if not (self.coord_zero.longitude <= coord.longitude <= self.coord_one.longitude):
            raise ValueError('Longitude %f is off the scale.' % (coord.longitude,))
         if not (self.coord_one.latitude <= coord.latitude <= self.coord_zero.latitude):
            raise ValueError('Latitude %f is off the scale.' % (coord.latitude,))

      coord_relative = coord - self.coord_zero
      return (coord_relative.longitude*self.factor_x, coord_relative.latitude*self.factor_y)




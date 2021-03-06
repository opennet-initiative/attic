#!/usr/bin/env python
#Copyright 2004,2005,2006,2007 Sebastian Hagen
# This file is part of py_selflib.

# py_selflib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# py_selflib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with py_selflib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import socket
import select
import time
import types
import logging
import signal
import thread
import re
import popen2
import signal
from sets import Set as set
import warnings

try:
   import fcntl
except ImportError:
   print 'Unable to import fcntl. File locking will not be available.'
   fcntl = None

try:
   import termios
except ImportError:
   print 'Unable to import termios. Termios style io control will be disabled.'
   termios = None
   
from process_reload import picklablesocket as socket_object

logger = logging.getLogger('socket_management')

class fd_wrap:
   logger = logging.getLogger('socket_management.fd_wrap')
   readable = []
   writable = []
   errable = []
   def __init__(self, fd, parent, file=None):
      self.fd = fd
      self.parent = parent
      self.file = file
      
   def fileno(self):
      return self.fd
   
   def __int__(self):
      return self.fd

   def __eq__(self, other):
      return (isinstance(other, self.__class__) and (self.fd == other.fd))
   
   def __ne__(self, other):
      return (not self.__eq__(other))

   def __cmp__(self, other):
      if (self.fd < other.fd):
         return -1
      if (self.fd > other.fd):
         return 1
      if (self.fd == other.fd):
         return 0

   def __hash__(self):
      return hash(self.fd)
   
   def fd_read(self):
      """Process readability event"""
      self.parent.fd_read(self)
      
   def fd_write(self):
      """Process writability event"""
      self.parent.fd_write(self)
      
   def fd_err(self):
      """Process error event."""
      self.parent.fd_err(self)
   
   def fd_register(self, seq):
      """Add fd to a specified event waiter sequence"""
      if (self in seq):
         raise StandardError('%r is already contained in seq %r.' % (self, seq))
      seq.append(self)
   
   def fd_unregister(self, seq):
      """Remove fd from specified event waiter sequence"""
      seq.remove(self)
   
   def fd_unregister_all(self):
      """Remove fd from all event sets"""
      for seq in (self.readable, self.writable, self.errable):
         if (self in seq):
            self.fd_unregister(seq)
      
   def fd_register_read(self):
      """Add fd to read set"""
      self.fd_register(self.readable)
      
   def fd_register_write(self):
      """Add fd to write set"""
      self.fd_register(self.writable)
   
   def fd_register_err(self):
      """Add fd to error set"""
      self.fd_register(self.errable)
   
   def fd_unregister_read(self):
      """Remove fd from read set"""
      self.fd_unregister(self.readable)
      
   def fd_unregister_write(self):
      """Remove fd from write set"""
      self.fd_unregister(self.writable)
   
   def fd_unregister_err(self):
      """Remove fd from err set"""
      self.fd_unregister(self.errable)
   
   def fd_registered_read(self):
      return (self in self.readable)
   
   def fd_registered_write(self):
      return (self in self.writable)
   
   def fd_registered_err(self):
      return (self in self.errable)
   
   def close(self):
      """Close fd, make parent forget about us, and forget about any and all associations"""
      if (not self):
         raise ValueError("%r has been closed earlier. Leave me alone." % (self,))
      self.logger.log(25, 'Shutting down %r.' % (self,))
      self.fd_unregister_all()
      if (self.file):
         if (isinstance(self.file, socket.socket)):
            try:
               self.file.shutdown(2)
            except socket.error:
               pass
         self.file.close()

      else:
         try:
            os.close(self.fd)
         except OSError:
            pass
      
      if (self.parent):
         self.parent.fd_forget(self)

      self.fd = None
   
   def __nonzero__(self):
      return bool(self.fd)
   
   def __repr__(self):
      return '%s(%r, %r)' % (self.__class__.__name__, self.fd, self.parent)


class asynchronous_transfer_base:
   input_handler = None
   def __init__(self):
      self.logger = None
      self.obtain_logger(self.__class__.__name__)

      self.buffers_input = {}
      self.buffers_output = {}
      self.close_handler = None

      self.address = None
      self.target = None

   def connection_up(self):
      return bool(self.buffers_input)

   def obtain_logger(self, name=None):
      if (name):
         self.loggername = name
      else:
         self.loggername = self.__class__.__name__
      if ((not (isinstance(self.logger, logging.Logger) or isinstance(self.logger, logging.RootLogger))) or (self.logger.name != self.loggername)):
         self.logger = logging.getLogger(self.loggername)

   def fd_err(self, fd):
      """Deal with ready for input/output and error conditions on waitable objects."""

      if not ((fd in self.buffers_output) or (fd in self.buffers_input)):
         self.logger.log(40, "This instance (%s; to %s) is not responsible for errable fd %s passed to fd_err. Trying to close it anyway." % (self, self.target, fd))
         
      fd.close()

   def fd_read(self, fd):
      """Read and buffer input"""
      if not (fd in self.buffers_input):
         raise ValueError('Fd %s is not in self.buffers_input' % (fd,))
      try:
         #select may fail with EBADF ("Bad file descriptor")
         while (len(select.select([fd],[],[],0)[0]) > 0):
            #os.read may fail with OSError: [Errno 104] Connection reset by peer
            new_data = os.read(int(fd), 1048576)
            if (len(new_data) > 0):
               self.buffers_input[fd] += new_data
            else:
               self.clean_up()
               break
      
      except (socket.error, OSError):
         self.logger.log(30, 'Error reading from fd %s connected to %s. Closing connection. Error:' % (fd, self.target), exc_info=True)
         self.clean_up()

      if ((fd in self.buffers_input) and (self.buffers_input[fd])):
         self.input_process(fd)

   def input_process(self, fd):
      """Process newly buffered input"""
      raise NotImplementedError('input_process should by implemented by child classes.')

   def fd_write(self, fd):
      """Write as much buffered output to specified fd as possible"""
      if not (fd in self.buffers_output):
         raise ValueError('Instance %r is not currently managing fd %r.' % (self, fd))
      
      buffer_output = self.buffers_output[fd]
      if (len(buffer_output) > 0):
         #Ok, we have something to send and the socket claims to be ready.
         try:
            #select may fail with EBADF ("Bad file descriptor")
            while (len(select.select([],[fd],[],0)[1]) > 0):
               #os.write could potentially fail with OSError: [Errno 104] Connection reset by peer
               bytes_sent = os.write(fd, buffer_output)
               if (bytes_sent >= len(buffer_output)):
                  #We are done here. Nothing to send left.
                  self.buffers_output[fd] = buffer_output = ''
                  break
               elif (bytes_sent > 0):
                  buffer_output = self.buffers_output[fd] = buffer_output[bytes_sent:]
               else:
                  #Connection has been closed
                  buffer_output = ''
                  self.fd_shutdown_error_write(fd)
                  break
               
         except (socket.error, OSError, select.error):
            self.logger.log(30, 'Error writing to socket connected to %s. Closing connection. Error:' % (self.address,), exc_info=True)
            self.buffers_output[fd] = buffer_output = ''
            self.fd_shutdown_error_write(fd)

         if (len(buffer_output) < 1):
            #We managed to clear our output buffer. Remove this fd from the global potentially_writeable_object-list to avoid a busy loop.
            try:
               fd.fd_unregister_write()
            except ValueError:
               pass

   def fd_shutdown_error_write(self, fd):
      del(self.buffers_output[fd])
      if (fd in self.buffers_input):
         self.fd_read(fd)
      fd.close()

   def send_data(self, data, fd=None):
      """Send data to our waitable object."""
      if (not self.buffers_output):
         self.logger.log(30, "Unable to output '%s'(to %s) since I don't currently have any open output objects." % (data.rstrip('\n'), self.target))
         return False
      elif (fd is None):
         #automatic selection; should at least work as long as there is exactly one
         fd = self.buffers_output.keys()[0]
      elif (fd not in self.buffers_output):
         self.logger.log(30, "Unable to output '%s' to '%s'(%s) since I don't have that fd open." % (data.rstrip('\n'), fd, self.target))
         return False
         
      self.logger.log(10, '< ' + repr(data))
      self.buffers_output[fd] = self.buffers_output[fd] + data

      self.fd_write(fd)
      if ((fd in self.buffers_output) and (self.buffers_output[fd])):
         try:
            fd.fd_register_write()
         except StandardError:
            pass

   def shutdown(self):
      """Try to flush as much output as we immediately can, then clean up."""
      for fd in self.buffers_output:
         self.fd_write(fd)

      self.clean_up()

   def fd_forget(self, fd):
      """Forget a transfer object."""
      if (callable(self.close_handler)):
         self.close_handler(fd)
      
      if (fd in self.buffers_input):
         if (self.buffers_input[fd]):
            self.input_process(fd)
         del(self.buffers_input[fd])
      
      if (fd in self.buffers_output):
         del(self.buffers_output[fd])

   def clean_up(self):
      """Shutdown all fds and discard remaining buffered output."""
      for fd in (self.buffers_output.keys() + self.buffers_input.keys()):
         if (fd):
            fd.close()


class sock_stream_connection_binary(asynchronous_transfer_base):
   def connection_init(self, address, address_family=socket.AF_INET):
      """Open a tcp connection to the target ip and port."""
      self.logger.log(10, 'Connecting to %s.' % (address,))
      self.target = self.address = address
      socket_new = socket_object(address_family, socket.SOCK_STREAM)
      socket_new.connect(address)
      socket_new.setblocking(0)
      fd = fd_wrap(socket_new.fileno(), self, socket_new)
      self.buffers_input[fd] = ''
      self.buffers_output[fd] = ''
      fd.fd_register_read()

   def input_process(self, fd):
      if (self.input_handler):
         self.input_handler()


class sock_stream_connection_linebased(sock_stream_connection_binary):
   def __init__(self, line_delimiters=['\n']):
      sock_stream_connection_binary.__init__(self)
      self.line_delimiters = line_delimiters
      self.buffer_lines = []

   def input_process(self, fd):
      """Process input in the value of the first element (as returned by .keys()) of the self.buffers_input-dictionary."""
      lines_split = [self.buffers_input[fd]]
      line_finished = False
      for line_delimiter in self.line_delimiters:
         lines_split_old = lines_split[:]
         lines_split = []
         for data_fragment in lines_split_old:
            lines_split.extend(data_fragment.split(line_delimiter))

      if (len(lines_split) > 0):
         #If the string ends with a line_delimiter, the last splitted element will be an empty string, 
         #otherwise it will contain the rest of the incomplete line. This code works in both cases.
         self.buffers_input[fd] = lines_split.pop(-1)
         
         self.buffer_lines.extend(lines_split)
         sock_stream_connection_binary.input_process(self, fd)
      else:
         assert (len(self.buffers_input[fd]) == 0)


class sock_server:
   logger = logging.getLogger('socket_listen')
   """Tcp server socket class. Accepts connections and instantiates their classes as needed."""
   def __init__(self, bindargs, handler, connection_class=sock_stream_connection_linebased, address_family=socket.AF_INET, socket_type=socket.SOCK_STREAM, backlog=2):
      self.backlog = backlog
      self.handler = handler
      self.connection_class = connection_class
      self.bindargs = bindargs
      self.address_family = address_family
      self.socket_type = socket_type
      self.backlog = backlog
      self.socket_init()

   def socket_init(self):
      """Open the server socket, set its options and register the fd."""
      self.socket = socket_object(self.address_family, self.socket_type)
      self.socket.bind(*self.bindargs)
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.socket.listen(self.backlog)
      self.fd = fd = fd_wrap(self.socket.fileno(), self, self.socket)
      fd.fd_register_read()
      
   def fd_read(self, fd):
      """Accept a new connection on socket fd."""
      if not (fd == self.fd):
         raise ValueError('Not responsible for fd %s.' % (fd,))
      
      new_socket, new_socket_address = self.socket.accept()
      if (callable(self.handler)):
         new_connection = self.connection_class()
         new_fd = fd_wrap(new_socket.fileno(), new_connection, new_socket)
         new_connection.buffers_input[new_fd] = ''
         new_connection.buffers_output[new_fd] = ''
         new_fd.fd_register_read()
         
         new_connection.target = new_connection.address = new_socket_address
         self.handler(connection = new_connection)

      else:
         self.logger(40, 'Unable to use new connection; no handler set. Closing it.')
         new_socket.close()

   def shutdown(self):
      self.clean_up()
      
   def clean_up(self):
      fd = self.fd
      fd.close()
      self.fd = None
      self.socket = None

      
class sock_nonstream(asynchronous_transfer_base):
   def connection_init(self, sock_protocol, address_family=socket.AF_INET, sock_type=socket.SOCK_DGRAM, bind_target=None):
      """Open a socket to the target ip."""
      socket_new = socket_object(sock_af, sock_type, sock_protocol)
      socket_new.setblocking(0)
      if (bind_target != None):
         socket_new.bind(bind_target)
      fd = fd_wrap(socket_new.fileno(), self, socket_new)
      self.socket = socket_new
      self.buffers_input[fd] = ''
      self.buffers_output[fd] = ''
      fd.fd_register_read()

   def fd_read(self, fd):
      sock = fd.file
      try:
         #select may fail with EBADF ("Bad file descriptor")
         while (len(select.select([fd],[],[],0)[0]) > 0):
            (data, source) = sock.recvfrom(1048576,)
            if (len(data) > 0):
               self.input_process(fd, source, data)
            else:
               self.close(fd)
               self.clean_up()
               break
      
      except socket.error:
         self.logger.log(30, 'Error reading from fd %s connected to %s. Closing connection. Error:' % (fd, self.target,), exc_info=True)
         self.clean_up()

      if ((fd in self.buffers_input) and (self.buffers_input[fd])):
         self.input_process(fd, source, data)

   def input_process(self, fd, source, data):
      raise NotImplementedError
         
   def fd_write(self, fd):
      raise NotImplementedError
   
   def send_data(self, data, target, fd=None, flags=0):
      """Send data to our waitable object."""
      if (not self.buffers_output):
         self.logger.log(30, "Unable to output %r(to %r) since I don't currently have any open output objects." % (data, target))
         raise StandardError("Unable to output %r(to %r) since I don't currently have any open output objects." % (data, target))
      if (fd == None):
         #automatic selection; should at least work as long as there is only one
         fd = self.buffers_output.keys()[0]
      
      self.logger.log(10, '%r< %r' % (target, data))
      return fd.file.sendto(data, flags, target)
      

class file_asynchronous_binary(asynchronous_transfer_base):
   """Asynchronous interface to pseudo-files"""
   def __init__(self, filename, input_handler, close_handler, mode=0777, flags=os.O_RDWR):
      asynchronous_transfer_base.__init__(self)
      self.input_handler = input_handler
      self.close_handler = close_handler
      self.target = self.filename = filename
      self.flags = flags = flags | os.O_NONBLOCK | os.O_NOCTTY
      self.fd = fd_wrap(os.open(filename, flags, mode), self)
      self.buffers_input[self.fd] = ''
      self.buffers_output[self.fd] = ''
      self.fd.fd_register_read()
      self.locked = False

   def input_process(self, fd):
      if (callable(self.input_handler)):
         self.input_handler(self, fd)
         
   def lockf(self, operation=None, *args, **kwargs):
      if not (fcntl):
         raise RuntimeError("fcntl module not present; perhaps the OS doesn't support it?")
      if not (operation):
         operation = fcntl.LOCK_EX

      return_value = fcntl.lockf(self.fd, operation, *args, **kwargs)
      self.locked = True
      self.logger.log(20, 'Locked fd %s on file %s.' % (self.fd, self.filename))
      return return_value
      
   def fd_forget(self, fd):
      if (self.locked and (fd == self.fd)):
         try:
            fcntl.lockf(fd, fcntl.LOCK_UN)
            self.locked = False
         except:
            self.logger.log(40, 'Failed to unlock fd %s on file %s. Error:' % (self.fd, self.filename), exc_info=True)
      
      asynchronous_transfer_base.fd_forget(self,fd)
      self.fd = None

   def clean_up(self):
      self.fd.close()
      
class serialport_asynchronous_binary(file_asynchronous_binary):
   def __init__(self, filename='/dev/ttyS0', *args, **kwargs):
      if not (termios):
         raise RuntimeError("termios module not present; perhaps the os doesn't support it?")

      file_asynchronous_binary.__init__(self, filename, *args, **kwargs)
      
   def tcgetattr(self):
      if (self.fd):
         return termios.tcgetattr(self.fd)
         
   def tcsetattr(self, when, attributes):
      if (self.fd):
         return termios.tcsetattr(self.fd, when, attributes)
         
   def tcsendbreak(self, duration):
      if (self.fd):
         return termios.tcsendbreak(self.fd, duration)
         
   def tcdrain(fd):
      if (self.fd):
         return termios.tcdrain(self.fd)
         
   def tcflush(self, queue):
      if (self.fd):
         return termios.tcflush(self.fd, queue)
         
   def tcflow(self, action):
      if (self.fd):
         return termios.tcflow(self.fd, action)
      
   def fd_forget(self, fd):
      if (fd):
         try:
            termios.tcflush(int(fd), termios.TCOFLUSH)
         except termios.error:
            pass
         file_asynchronous_binary.fd_forget(self, fd)

#pipes to spawned processes
CHILD_REACT_NOT = 0
CHILD_REACT_WAIT = 1
CHILD_REACT_KILL = 2

class child_execute_base(asynchronous_transfer_base):
   """Base class for piped child-spawning."""
   def __init__(self, command, input_handler, close_handler, termination_handler, finish=1):
      asynchronous_transfer_base.__init__(self)
      
      self.command = command
      self.input_handler = input_handler
      self.close_handler = close_handler
      self.termination_handler = termination_handler
      self.finish = finish

      self.stdin_fd = None
      self.stdout_fd = None
      self.stderr_fd = None
      self.child = None

      self.stdout_str = None
      self.stderr_str = None
      self.child_spawn()
      
   def child_spawn(self):
      raise NotImplementedError('child_spawn should be implemented by child classes.')
      
   def input_process(self, fd):
      if (self.input_handler):
         self.input_handler(self, fd)
         
   def child_kill(self, sig=signal.SIGTERM):
      """Send a signal (SIGTERM by default) to our child process."""
      if (self.child):
         self.logger(30, 'Sending signal %s to process spawned by executing "%s".' % (sig, self.command,))
         os.kill(self.child.pid, sig)

   def child_poll(self):
      """Check if our child is dead, and if so poll() on it, wait() on it and if termination_handler is callable call it with the results."""
      if (self.child):
         return_code = self.child.poll()
         if (return_code == -1):
            #Process is still alive
            return False
         else:
            exit_status = self.child.wait()
            self.logger.log(20, 'Process %d spawned by executing "%s" has finished with return code %s and exit status %s.' % (self.child.pid, self.command, return_code, exit_status))
            if (callable(self.termination_handler)):
               self.termination_handler(self, return_code, exit_status)
            
            self.clean_up()

   def fd_forget(self, fd):
      if (fd == self.stdin_fd):
         self.stdin_fd = None
      if (fd == self.stdout_fd):
         self.stdout_fd = None
         self.stdout_str = self.buffers_input[fd]
      if (fd == self.stderr_fd):
         self.stderr_fd = None
         self.stderr_str = self.buffers_input[fd]
      
      asynchronous_transfer_base.fd_forget(self, fd)
      if (len(self.buffers_input) == 0 == len(self.buffers_output)):
         #We're out of open input fds.
         self.child_poll()
         if (self.child):
            #And our child is still alive,...
            if (self.finish == CHILD_REACT_WAIT):
               #...so we WAIT for it.
               self.logging.log(30, 'Child process %d (resulted from executing "%s") has closed all connections to us, but is still active. Spawning thread to wait for it.' % (self.child.pid, self.command))
               self.thread = threading.Thread(group=None, target=self.wait_child_childthread, name=None, args=(), kwargs={})
               self.thread.setDaemon(True)
               self.thread.start()
            elif (self.finish == CHILD_REACT_KILL):
               #...so we kill it.
               sig = signal.SIGKILL
               self.child_kill(sig)
               self.child_poll()
               if (self.child):
                  self.logger.log(45, 'Child process %d (resulted from executing "%s") has survived signal %d sent by us. Giving up.' % (self.child.pid, self.command, sig))
   
   def wait_child_childthread(self):
      """Wait() on our child, then poll() it, set a timer to report the results and finally trigger pipe_notify."""
      exit_status = self.child.wait()
      return_code = self.child.poll()
      Timer(interval=-1000, function=self.termination_handler, args=(self, return_code, exit_status), callback_kwargs={}, parent=None)
      socket_management.pipe_notify.notify()

   def stream_record(self, name, fd, in_stream=False):
      """Prepare internal data structures for a new stream and register its fd."""
      self.__dict__[name] = fd
      if (in_stream):
         self.buffers_input[fd] = ''
         fd.fd_register_read()
      else:
         self.buffers_output[fd] = ''
      
   def clean_up(self):
      asynchronous_transfer_base.clean_up(self)
      self.child = None

class child_execute_Popen3(child_execute_base):
   '''Popen3 objects provide stdin, stdout, and stderr of the child process.'''
   def __init__(self, capturestderr=False, *args, **kwargs):
      self.capturestderr = capturestderr
      child_execute_base.__init__(self, *args, **kwargs)
      
   def child_spawn(self):
      self.child = child = popen2.Popen3(self.command, self.capturestderr)
      self.stream_record('stdin_fd', fd_wrap(child.tochild.fileno(), self), in_stream=False)
      self.stream_record('stdout_fd', fd_wrap(child.fromchild.fileno(), self), in_stream=True)
      
      if (child.childerr):
         self.stream_record('stderr_fd', fd_wrap(child.childerr.fileno(), self), in_stream=True)

class child_execute_Popen4(child_execute_base):
   '''Popen4 objects provide stdin to the child process, and a combined stdout+stderr stream from it.'''
   def child_spawn(self):
      self.child = child = popen2.Popen4(self.command)
      fd_out = fd_wrap(child.fromchild.fileno(), self)
      
      self.stream_record('stdin_fd', fd_wrap(child.tochild.fileno(), self), in_stream=False)
      self.stream_record('stdout_fd', fd_out, in_stream=True)
      self.stderr_fd = fd_out


class pipe_notify_class:
   """Manages a pipe used to safely interrupt blocking select calls of other threads."""
   logger = logging.getLogger('socket_management.pipe_notify')
   def __init__(self):
      self.read_fd = self.write_fd = None
      #waitable_object_instances_add(self)
      self.pipe_init()

   def pipe_init(self):
      """Open and initialize the pipe,"""
      (read_fd, self.write_fd) = [fd_wrap(fd, self) for fd in os.pipe()]
      fcntl.fcntl(read_fd, fcntl.F_SETFL, os.O_NONBLOCK)
      read_fd.fd_register_read()
      self.read_fd = read_fd
      
   def fd_read(self, fd):
      """Read data and throw it away. Reestablish pipe if it has collapsed."""
      if not (fd == self.read_fd):
         raise ValueError('Not responsible for fd %s' % (fd,))
      
      while (len(select.select([fd],[],[],0)[0]) > 0):
         if (len(os.read(int(fd), 1048576)) <= 0):
            #looks like for some reason this pipe has collapsed.
            self.logger.log(40, 'The pipe has collapsed. Reinitializing.')
            self.clean_up()
            self.pipe_init()

   def notify(self):
      """Write a byte into the input end of the pipe if pipe intact and not already readable"""
      if ((self.read_fd) and (self.write_fd) and ((len(select.select([self.read_fd],[],[],0)[0])) == 0)):
         os.write(int(self.write_fd), '\000')

   def fd_forget(self, fd):
      if (self.read_fd == fd):
         self.read_fd = None
      elif (self.write_fd == fd):
         self.write_fd = None
      
      if (self.read_fd):
         self.read_fd.close()
      if (self.write_fd):
         self.write_fd.close()
   
   def shutdown(self):
      self.clean_up()
      
   def clean_up(self):
      self.fd_forget(None)


TIMERS_CALLBACK_HANDLER = 2
TIMERS_PARENT = 1

class Timer:
   '''Timer class; instantiate to start. This is one of the few thread-safe parts of socket_management,
      because it's also used to transfer Information in general back to the main thread.'''
   logger = logging.getLogger('socket_management.Timer')
   lock = thread.allocate_lock()
   timers_active = []
   def __init__(self, interval, function, parent=None, args=(), kwargs={}, persistence=False, align=False):
      self.interval = interval
      self.function = function
      self.parent = parent
      self.args = args
      self.kwargs = kwargs
      self.persistence = bool(persistence)
      self.align = align
      
      if (align):
         interval -= (time.time() % interval)
 
      self.expire_ts = time.time() + float(interval)
      self.register()

   def __cmp__(self, other):
      if (self.expire_ts < other.expire_ts):
         return -1
      if (self.expire_ts > other.expire_ts):
         return 1
      if (self.expire_ts == other.expire_ts):
         return 0

   def register(self):
      self.logger.log(15, 'Registering timer %r.' % (self,))
      self.lock.acquire()
      try:
         self.timers_active.append(self)
         self.timers_active.sort()
      finally:
         self.lock.release()
      
   def unregister(self):
      self.logger.log(15, 'Unregistering timer %r.' % (self,))
      self.lock.acquire()
      try:
         self.timers_active.remove(self)
      finally:
         self.lock.release()

   def function_call(self):
      self.logger.log(20, 'Executing timer %r.' % (self,))
      self.function(*self.args, **self.kwargs)
      
   def expire_ts_bump(self):
      if (not self.persistence):
         raise ValueError("%r isn't persistent." % self)
      
      now = time.time()
      
      self.expire_ts = now + self.interval
      if (self.align):
         self.expire_ts -= now % self.interval

   def __getinitargs__(self):
      return (self.interval, self.function, self.parent, self.args, self.kwargs, self.persistence, self.align)

   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, self.__getinitargs__())
   
   def __str__(self):
      return '%s%s' % (self.__class__.__name__, self.__getinitargs__())

   def stop(self):
      self.logger.log(20, 'Stopping timer %r.' % (self,))
      self.unregister()

   def timers_process(cls):
      cls.lock.acquire()
      timers_active = cls.timers_active
      order_change = False
      expired_timers = []
      try:
         while (timers_active and (timers_active[0].expire_ts <= time.time())):
            timer = timers_active.pop(0)
            expired_timers.append(timer)
            if (timer.persistence):
               timer.expire_ts_bump()
               timers_active.append(timer)
               order_change = True

         if (order_change):
            timers_active.sort()

      finally:
         cls.lock.release()
      
      for expired_timer in expired_timers:
         try:
            expired_timer.function_call()
         except:
            cls.logger.log(40, 'Exception in Timer %r: ', exc_info=True)
            
   timers_process = classmethod(timers_process)
   
   def timers_stop_byattribute(cls, attr_name, attr_val):
      cls.lock.acquire()
      try:
         for timer in cls.timers_active[:]:
            if (getattr(timer,attr_name) == attr_val):
               timer.stop()
      finally:
         cls.lock.release()

   timers_stop_byattribute = classmethod(timers_stop_byattribute)

   def timers_stop_byfunction(cls, function):
      cls.timers_stop_byattribute(cls, 'function', function)
      
   timers_stop_byfunction = classmethod(timers_stop_byfunction)
      
   def timers_stop_byparent(cls, parent):
      cls.timers_stop_byattribute(cls, 'parent', parent)

   timers_stop_byparent = classmethod(timers_stop_byparent)

   def timers_stop_all(cls):
      cls.logger.log(16, 'Unregistering all active timers.')
      cls.lock.acquire()
      try:
         del(cls.timers_active[:])
      finally:
         cls.lock.release()

   timers_stop_all = classmethod(timers_stop_all)

def timers_add(delay, callback_handler, parent=None, args=(), kwargs={}, persistence=False):
   """DEPRECATED: Add a timer to the list of running timers."""
   warnings.warn("socket_management.timers_add() is deprecated; use the Timer class instead")
   return Timer(delay, callback_handler, parent, args, kwargs, persistence, persistence)

def timers_remove(timer_entry):
   """DEPRECATED: Remove the timer matching the timer_entry from running timers, if it is one."""
   warnings.warn("socket_management.timers_remove() is deprecated; use the timer.close() instead")
   timer_entry.stop()

def timers_remove_all(data_type, data):
   """Remove all timers with a specific callback_handler or parent."""
   warnings.warn("socket_management.timers_remove_all() is deprecated; use Timer.timers_stop_by* instead")
   if (data_type == TIMERS_CALLBACK_HANDLER):
      Timer.timers_stop_byfunction(data)
   elif (data_type == TIMERS_PARENT):
      Timer.timers_stop_byparent(data)
   else:
      raise ValueError("Invalid argument %s for data_type (expected integer 1 or 2)." % repr(data_type))


def select_loop():
   """Run the (potentially) infinite main select loop. Should be called as the last step in program intizialization."""
   fds_readable = fd_wrap.readable
   fds_writable = fd_wrap.writable
   fds_errable = fd_wrap.errable
   
   wo_type_readable = 0
   wo_type_writable = 1
   wo_type_errable = 2
   
   while (1):
      if (not Timer.timers_active):
         if ([] == fds_readable == fds_writable == fds_errable):
            logger.log(30, 'No waitable objects or timers left active. Leaving select loop.')
            return None
         
         timeout = None
      else:
         timeout = max((Timer.timers_active[0].expire_ts - time.time()), 0)

      fds_readable_now, fds_writable_now, fds_errable_now = select.select(fds_readable, fds_writable, fds_errable, timeout)

      for (waiting_fd_list, wo_type) in ((fds_readable_now,wo_type_readable), (fds_writable_now,wo_type_writable), (fds_errable_now,wo_type_errable)):
         for fd in waiting_fd_list:
            try:
               if (wo_type is wo_type_readable):
                  fd.fd_read()
               elif (wo_type is wo_type_writable):
                  fd.fd_write()
               elif (wo_type is wo_type_errable):
                  fd.fd_err()
            except Exception:
               if (fd):
                  logger.log(40, 'Failed to process fd %r in mode %r. Trying to close. Error:' % (fd, wo_type), exc_info=True)
                  try:
                     fd.close()
                  except OSError:
                     pass

      Timer.timers_process()

def shutdown():
   """Shut down all connections managed by this module and clear the timer list."""
   for fd in (fd_wrap.readable + fd_wrap.writable + fd_wrap.errable):
      if (fd):
         fd.close()
         
   Timer.timers_stop_all()


   
pipe_notify = pipe_notify_class()

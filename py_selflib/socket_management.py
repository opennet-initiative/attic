#!/usr/bin/env python2.3
#Copyright 2004 Sebastian Hagen
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
   
import init_misc

defaults = {}
defaults['class_defaults'] = {}
defaults['waitable_objects'] = [[],[],[]]
defaults['waitable_object_data'] = {}
defaults['waitable_object_cache_state'] = {
   'updated':0
   }

defaults['running_timers'] = []
defaults['timer_parents'] = {}
defaults['locks'] = {}

init_misc.set_defaults(defaults=defaults, global_scope=globals())

locks['timers'] = thread.allocate_lock()

logger = logging.getLogger('socket_management')

fds_readable = []
fds_writable = []
fds_erring = []


class asynchronous_transfer_base:
   input_handler = None
   def __init__(self):
      self.logger = None
      self.obtain_logger(self.__class__.__name__)

      self.buffers_input = {}
      self.buffers_output = {}
      self.file_objects = {}
      self.close_handler = None

      self.address = None
      self.target = None

   def obtain_logger(self, name=None):
      if (name):
         self.loggername = name
      else:
         self.loggername = self.__class__.__name__
      if ((not (isinstance(self.logger, logging.Logger) or isinstance(self.logger, logging.RootLogger))) or (self.logger.name != self.loggername)):
         self.logger = logging.getLogger(self.loggername)

   def fd_err(self, fd):
      """Deal with ready for input/output and errro conditions on waitable objects."""

      if not ((fd in self.buffers_output) or (fd in self.buffers_input)):
         self.logger.log(40, "This instance (%s; to %s) is not responsible for erring_fd %s passed to fd_err. Trying to close it anyway." % (self, self.target, fd))
         
      self.close(erring_object)

   def fd_read(self, fd):
      if not (fd in self.buffers_input):
         raise ValueError('Fd %s is not in self.buffers_input' % (fd,))
      try:
         #select may fail with EBADF ("Bad file descriptor")
         while (len(select.select([fd],[],[],0)[0]) > 0):
            #os.read may fail with OSError: [Errno 104] Connection reset by peer
            new_data = os.read(fd, 1048576)
            if (len(new_data) > 0):
               self.buffers_input[fd] += new_data
            else:
               self.close(fd)
               self.clean_up()
               break
      
      except (socket.error, OSError):
         self.logger.log(30, 'Error reading from fd %s connected to %s. Closing connection. Error:' % (fd, self.target,), exc_info=True)
         self.clean_up()

      if ((fd in self.buffers_input) and (self.buffers_input[fd])):
         self.input_process(fd)

   def input_process(self, fd):
      raise NotImplementedError('input_process should by implemented by child classes.')

   def fd_register(self, fd):
      '''Check whether there is an entry for this fd in wo_instances that points to us, and if not, make one.'''
      if ((not fd in wo_instances.key_list) or (wo_instances[fd] != self)):
         wo_instances[fd] = self
      
   def fd_unregister(self, fd):
      if ((fd in wo_instances.key_list) and (wo_instances[fd] == self)):
         del(wo_instances[fd])
         if (fd in fds_readable):
            fds_readable.remove(fd)
         if (fd in fds_writable):
            fds_writable.remove(fd)
         if (fd in fds_erring):
            fds_erring.remove(fd)
         
   def fd_write(self, fd):
      if not (fd in self.buffers_output):
         if (fd in fds_writable):
            fds_writable.remove(fd)
         return False
      
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
                  self.socket_shutdown_error_write(fd)
                  break
               
         except (socket.error, OSError):
            self.logger.log(30, 'Error writing to socket connected to %s. Closing connection. Error:' % (self.address,), exc_info=True)
            self.buffers_output[fd] = buffer_output = ''
            self.socket_shutdown_error_write(writable_object)

         if (len(buffer_output) < 1):
            #We managed to clear our output buffer. Remove this socket from the global potentially_writeable_object-list to avoid a busy loop.
            if (fd in fds_writable):
               fds_writable.remove(fd)

   def socket_shutdown_error_write(self, fd):
      del(self.buffers_output[fd])
      if (fd in self.buffers_input):
         self.fd_read(fd)
      self.close(fd)

   def send_data(self, data, fd=None):
      """Send data to our waitable object."""
      if (not self.buffers_output):
         self.logger.log(30, "Unable to output '%s'(to %s) since I don't currently have any open output objects." % (data.rstrip('\n'), self.target))
         return False
      elif (fd is None):
         #automatic selection; should at least work as long as there is only one
         fd = self.buffers_output.keys()[0]
      elif (fd not in self.buffers_output):
         self.logger.log(30, "Unable to output '%s' to '%s'(%s) since I don't have that fd open." % (data.rstrip('\n'), fd, self.target))
         return False
         
      self.logger.log(10, '< ' + repr(data))
      self.buffers_output[fd] = self.buffers_output[fd] + data

      self.fd_write(fd)
      if ((fd in self.buffers_output) and (self.buffers_output[fd]) and (not fd in fds_writable)):
         fds_writable.append(fd)

   def shutdown(self):
      for fd in self.buffers_output:
         self.fd_write(fd)

      self.clean_up()

   def close(self, fd):
      """Close a transfer object."""
      self.logger.log(10, 'Closing fd %s which is an interface to %s.' % (fd, repr(self.target)))
      if (fd in self.file_objects):
         file_object = self.file_objects[fd]
         if (type(file_object) == socket.SocketType):
            try:
               file_object.shutdown(2)
            except socket.error:
               pass
            
            file_object.close()
      else:
         file_object = None
         try:
            os.close(fd)
         except OSError:
            pass

      if (fd in self.buffers_input):
         if (self.buffers_input[fd]):
            self.input_process(fd)
         del(self.buffers_input[fd])
         
      if (fd in self.buffers_output):
         del(self.buffers_output[fd])

      self.fd_unregister(fd)
            
      if (callable(self.close_handler)):
         self.close_handler(self, fd)

   def clean_up(self):
      for fd in (self.buffers_output.keys() + self.buffers_input.keys()):
         self.close(fd)


class sock_stream_connection_binary(asynchronous_transfer_base):
   def connection_init(self, address):
      """Open a tcp connection to the target ip and port."""
      self.logger.log(10, 'Connecting to %s.' % (address,))
      self.target = self.address = address
      socket_new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      socket_new.connect(address)
      socket_new.setblocking(0)
      fd = socket_new.fileno()
      self.file_objects[fd] = socket_new
      self.buffers_input[fd] = ''
      self.buffers_output[fd] = ''
      self.fd_register(fd)
      fds_readable.append(fd)

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
   """Tcp server socket class. Accepts connections and instantiates their classes as needed."""
   def __init__(self, port, handler, connection_class=sock_stream_connection_linebased, address_family=socket.AF_INET, socket_type=socket.SOCK_STREAM, host='', backlog=2):
      self.logger = logging.getLogger('socket_listen')
      self.backlog = backlog
      self.handler = handler
      self.connection_class = connection_class
      self.host = host
      self.port = port
      self.address_family = address_family
      self.socket_type = socket_type
      self.backlog = backlog
      self.socket_init()

   def socket_init(self):
      """Open the server socket, set its options and register the fd."""
      self.socket = socket.socket(self.address_family, self.socket_type)
      self.socket.bind((self.host, self.port))
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.socket.listen(self.backlog)
      self.fd = fd = self.socket.fileno()
      if ((not fd in wo_instances.key_list) or (wo_instances[fd] != self)):
         wo_instances[fd] = self
      if not (fd in fds_readable):
         fds_readable.append(fd)
      
   def fd_read(self, fd):
      """Accept a new connection on socket fd."""
      if not (fd == self.fd):
         raise ValueError('Not responsible for fd %s.' % (fd,))
      
      new_socket, new_socket_address = self.socket.accept()
      if (callable(self.handler)):
         new_fd = new_socket.fileno()
         new_connection = self.connection_class()
         new_connection.buffers_input[new_fd] = ''
         new_connection.buffers_output[new_fd] = ''
         new_connection.file_objects[new_fd] = new_socket
         new_connection.fd_register(new_fd)
         if not (new_fd in fds_readable):
            fds_readable.append(new_fd)
         
         new_connection.target = new_connection.address = new_socket_address
         self.handler(connection=new_connection)

      else:
         self.logger(40, 'Unable to use new connection; no handler set. Closing it.')
         new_socket.close()

   def shutdown(self):
      self.clean_up()
      
   def clean_up(self):
      fd = self.fd
      if ((fd in wo_instances.key_list) and (wo_instances[fd] == self)):
         del(wo_instances[fd])
         if (fd in fds_readable):
            fds_readable.remove(fd)
      os.close(fd)
      self.fd = None
      self.socket.close()
      self.socket = None

      
class sock_nonstream(asynchronous_transfer_base):
   def connection_init(self, sock_protocol, sock_af=socket.AF_INET, sock_type=socket.SOCK_DGRAM, bind_target=None):
      """Open a socket to the target ip."""
      socket_new = socket.socket(sock_af, sock_type, sock_protocol)
      socket_new.setblocking(0)
      if (bind_target != None):
         socket_new.bind(bind_target)
      fd = socket_new.fileno()
      self.socket = socket_new
      self.file_objects[fd] = socket_new
      self.buffers_input[fd] = ''
      self.buffers_output[fd] = ''
      self.fd_register(fd)
      fds_readable.append(fd)

   def fd_read(self, fd):
      if not (fd in self.file_objects):
         raise ValueError('Fd %s is not in self.file_objects' % (fd,))
      sock = self.file_objects[fd]
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
      if (not self.file_objects):
         self.logger.log(30, "Unable to output %r(to %r) since I don't currently have any open output objects." % (data, target))
         return False
      elif (fd == None):
         #automatic selection; should at least work as long as there is only one
         fd = self.buffers_output.keys()[0]
      elif (fd not in self.file_objects):
         self.logger.log(30, "Unable to output %r to %r(%r) since I don't have that fd open." % (data, fd, target))
         return False
         
      self.logger.log(10, '%r< %r' % (target, data))
      return self.file_objects[fd].sendto(data, flags, target)
      
      
class file_asynchronous_binary(asynchronous_transfer_base):
   """Asynchronous interface to pseudo-files"""
   def __init__(self, filename, input_handler, close_handler, mode=0777, flags=os.O_RDWR):
      asynchronous_transfer_base.__init__(self)
      self.input_handler = input_handler
      self.close_handler = close_handler
      self.target = self.filename = filename
      self.flags = flags = flags | os.O_NONBLOCK | os.O_NOCTTY
      self.fd = os.open(filename, flags, mode)
      self.fd_register(self.fd)
      self.buffers_input[self.fd] = ''
      self.buffers_output[self.fd] = ''
      fds_readable.append(self.fd)
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
      
   def close(self, fd):
      if (self.locked and (fd == self.fd)):
         try:
            fcntl.lockf(fd, fcntl.LOCK_UN)
            self.locked = False
         except:
            self.logger.log(40, 'Failed to unlock fd %s on file %s. Error:' % (self.fd, self.filename), exc_info=True)
      
      asynchronous_transfer_base.close(self, fd)
      self.fd = None

   def clean_up(self):
      self.close(self.fd)
      
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
      
   def close(self, fd):
      if (fd):
         try:
            termios.tcflush(fd, termios.TCOFLUSH)
         except termios.error:
            pass
         file_asynchronous_binary.close(self, fd)
         
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

   def close(self, fd):
      if (fd == self.stdin_fd):
         self.stdin_fd = None
      if (fd == self.stdout_fd):
         self.stdout_fd = None
         self.stdout_str = self.buffers_input[fd]
      if (fd == self.stderr_fd):
         self.stderr_fd = None
         self.stderr_str = self.buffers_input[fd]
      
      asynchronous_transfer_base.close(self, fd)

      if (len(self.buffers_input) == 0 == len(self.buffers_output)):
         #We're out of open fds.
         self.child_poll()
         if (self.child):
            #And our child is still alive,...
            if (self.finish == 1):
               #...so we WAIT for it.
               self.logging.log(30, 'Child process %d (resulted from executing "%s") has closed all connections to us, but is still active. Spawning thread to wait for it.' % (self.child.pid, self.command))
               self.thread = threading.Thread(group=None, target=self.wait_child_childthread, name=None, args=(), kwargs={})
               self.thread.setDaemon(True)
               self.thread.start()
            elif (self.finish == 2):
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
      socket_management.timers_add(delay=-1000, callback_handler=self.termination_handler, args=(self, return_code, exit_status), callback_kwargs={}, parent=None)
      socket_management.pipe_notify.notify()

   def stream_record(self, name, fd, in_stream=False):
      """Prepare internal data structures for a new stream and register its fd."""
      self.__dict__[name] = fd
      self.fd_register(fd)
      if (in_stream):
         self.buffers_input[fd] = ''
         if not (fd in fds_readable):
            fds_readable.append(fd)  
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
      self.stream_record('stdin_fd', child.tochild.fileno(), in_stream=False)
      self.stream_record('stdout_fd', child.fromchild.fileno(), in_stream=True)
      
      if (child.childerr):
         self.stream_record('stderr_fd', child.childerr.fileno(), in_stream=True)
         
class child_execute_Popen4(child_execute_base):
   '''Popen4 objects provide stdin to the child process, and a combined stdout+stderr stream from it.'''
   def child_spawn(self):
      self.child = child = popen2.Popen4(self.command)
      self.stream_record('stdin_fd', child.tochild.fileno(), in_stream=False)
      self.stream_record('stdout_fd', child.fromchild.fileno(), in_stream=True)
      self.stderr_fd = child.fromchild.fileno()


class pipe_notify_class:
   """Manages a pipe used to safely interrupt blocking select calls of other threads."""
   def __init__(self):
      self.logger = logging.getLogger('socket_management.pipe_notify')
      self.read_fd = self.write_fd = None
      #waitable_object_instances_add(self)
      self.pipe_init()

   def pipe_init(self):
      """Open and initialize the pipe,"""
      self.read_fd, self.write_fd = os.pipe()
      fcntl.fcntl(self.read_fd, fcntl.F_SETFL, os.O_NONBLOCK)
      
      read_fd = self.read_fd
      if ((not read_fd in wo_instances) or (wo_instances[read_fd] != self)):
         wo_instances[read_fd] = self
      if (not read_fd in fds_readable):
         fds_readable.append(read_fd)

   def fd_read(self, fd):
      """Read data and throw it away. Reastablish pipe if it has collapsed."""
      if not (fd == self.read_fd):
         raise ValueError('Not responsible for fd %s' % (fd,))
      
      while (len(select.select([fd],[],[],0)[0]) > 0):
         if (len(os.read(fd, 1048576)) <= 0):
            #looks like for some reason this pipe has collapsed.
            self.logger.log(40, 'The pipe has collapsed. Reinitializing.')
            self.clean_up_pipe()
            self.pipe_init()

   def notify(self):
      """Write a byte in to the input end of the pipe."""
      if ((self.read_fd) and (self.write_fd) and ((len(select.select([self.read_fd],[],[],0)[0])) == 0)):
         os.write(self.write_fd, '\000')

   def clean_up_pipe(self):
      for fd in (self.read_fd, self.write_fd):
         os.close(fd)
         if ((fd in wo_instances.key_list) and (wo_instances[fd] == self)):
            del(wo_instances[fd])
            if (fd in fds_readable):
               fds_readable.remove(fd)

      self.read_fd = self.write_fd = None

   def shutdown(self):
      self.clean_up()
      
   def clean_up(self):
      self.clean_up_pipe()

class wo_dictionary(dict):
   def __init__(self, *a, **ka):
      dict.__init__(self, *a, **ka)
      self.__cache_keys__()
   def __setitem__(self, *a, **ka):
      dict.__setitem__(self, *a, **ka)
      self.__cache_keys__()
   def __delitem__(self, *a,**ka):
      dict.__delitem__(self, *a,**ka)
      self.__cache_keys__()
   def clear(self,*a,**ka):
      dict.clear(self,*a,**ka)
      self.__cache_keys__()
   def fromkeys(self,*a,**ka):
      dict.fromkeys(self,*a,**ka)
      self.__cache_keys__()
   def setdefault(self,*a,**ka):
      dict.setdefault(self,*a,**ka)
      self.__cache_keys__()
   def pop(self,*a,**ka):
      dict.pop(self,*a,**ka)
      self.__cache_keys__()
   def popitem(self,*a,**ka):
      dict.popitem(self,*a,**ka)
      self.__cache_keys__()
   def __cache_keys__(self):
      self.key_list = self.keys()

wo_instances = wo_dictionary()

TIMERS_CALLBACK_HANDLER = 2
TIMERS_PARENT = 1

def timers_add(delay, callback_handler, parent=None, args=(), kwargs={}, persistence=False):
   """Add a timer to the list of running timers."""
   persistence = bool(persistence)
   
   if (persistence):
      persistence = delay
      delay = delay - (time.time() % delay)

   expire_ts = time.time() + float(delay)
   
   locks['timers'].acquire()
   try:
      running_timers.append((expire_ts, parent, callback_handler, args, kwargs, persistence))
      running_timers.sort()
   finally:
      locks['timers'].release()
      
   return (expire_ts, parent, callback_handler, args, kwargs, persistence)


def timers_remove(timer_entry):
   """Remove the timer matching the timer_entry from running timers, if it is one."""
   if (timer_entry in running_timers):
      locks['timers'].acquire()
      try:
         running_timers.remove(timer_entry)
      finally:
         locks['timers'].release()

def timers_remove_all(data_type, data):
   """Remove all timers with a specific callback_handler or parent."""
   if ((type(data_type) == int) and (0 < data_type < 3)):
      locks['timers'].acquire()
      try:
         for timer_entry in running_timers[:]:
            if (timer_entry[data_type] == data):
               running_timers.remove(timer_entry)

      finally:
         locks['timers'].release()

   else:
      raise ValueError("Invalid argument %s for data_type (expected integer 1 or 2)." % repr(data_type))

def timers_process():
   """Check for expired timers and process them."""
   order_change = False
   expired_timers = []
   locks['timers'].acquire()
   try:
      while ((len(running_timers) > 0) and (running_timers[0][0] <= time.time())):
         expired_timer = running_timers.pop(0)
         persistence = expired_timer[5]
         expired_timers.append(expired_timer)
         if (persistence):
            next_expire_ts = time.time() + persistence - (time.time() % persistence)
            running_timers.append((next_expire_ts,) + expired_timer[1:])
            order_change = True

      if ((order_change) and len(running_timers) > 0):
         running_timers.sort()
         
   finally:
      locks['timers'].release()
 
   for expired_timer in expired_timers:     
      try:
         expired_timer[2](*expired_timer[3], **expired_timer[4])
      except StandardError:
         logger.log(40, 'Exception in timer:', exc_info=True)


def select_loop():
   """Run the (potentially) infinite main select loop. Should be called as the last step in program intizialization."""
   while (1):
      if (len(running_timers) == 0):
         if ([] == fds_readable == fds_writable == fds_erring):
            logger.log(30, 'No waitable objects or timers left active. Leaving select loop.')
            return None
         
         timeout = None
      else:
         timeout = running_timers[0][0] - time.time()
         if (timeout < 0):
            timeout = 0

      fds_readable_now, fds_writable_now, fds_erring_now = select.select(fds_readable, fds_writable, fds_erring, timeout)

      for waiting_fd_list, wo_type in ((fds_readable_now,0), (fds_writable_now,1), (fds_erring_now,2)):
         for fd in waiting_fd_list:
            if (fd in wo_instances):
               instance = wo_instances[fd]
               if (wo_type == 0):
                  instance.fd_read(fd)
               elif (wo_type == 1):
                  instance.fd_write(fd)
               elif (wo_type == 2):
                  instance.fd_err(fd)
               
            else:
               logger.log(40, 'Unknown waitable fd %s returned by select.select() in list %s. Closing it.' % (waiting_object, list_index))
               try:
                  os.close(fd)
               except OSError:
                  pass
               for fd_list in (fds_readable, fds_writable, fds_erring):
                  if (fd in fd_list):
                     fd_list.remove(fd)
                     
      timers_process()

def shutdown():
   """Shut down ALL connections managed by this module and clear the timer list."""
   fds = []
   for fd in wo_instances.copy():
      if not (fd in fds):
         fds.append(fd)
         os.close(fd)
         del(wo_instances[fd])
         
   locks['timers'].acquire()
   try:
      running_timers = []
   finally:
      locks['timers'].release()

   
pipe_notify = pipe_notify_class()

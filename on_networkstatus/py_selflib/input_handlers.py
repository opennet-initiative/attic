#!/usr/bin/env python2.3
#Copyright to the py_selflib code 2004 Sebastian Hagen
# Most of the code overriding optparse class methods is copied from 
# the optparse included with python2.3


import logging
import optparse

class handlers_base:
   """Base class for input handlers. Not very useful by itself."""
   def __init__(self, parent, output, event_types, loggername=None):
      self.parent = parent
      self.output = output
      self.handlers = {}
      for event_type in event_types:
         self.handlers[event_type] = {}
      
      if (loggername):
         self.loggername = loggername
         self.logger = logging.getLogger(self.loggername)
   
   def add(self, event_type, event, handler, permissions=[]):
      """Register a handler."""
      if (not event_type in self.handlers):
         raise ValueError('Unknown event_type %s.' % repr(event_type))
      if (not (event in self.handlers[event_type])):
         self.handlers[event_type][event] = []
      if (not (handler in self.handlers[event_type][event])):
         self.handlers[event_type][event].append((handler, permissions))
         

   def remove(self, event_type, event, handler, permissions=[]):
      """Unregister a handler."""
      if ((event_type in self.handlers) and (event in self.handlers[event_type]) and ((handler, permissions) in self.handlers[event_type][event])):
         self.handlers[event_type][event].remove((handler, permissions))

         if (len(self.handlers[event_type][event]) == 0):
            del(self.handlers[event_type][event])

   def remove_all(self, handlers):
      for event_type in self.handlers:
         for event in self.handlers[event_type].keys():
            for handler in handlers:
               for handler_entry in self.handlers[event_type][event]:
                  if (handler == handler_entry[0]):
                     self.handlers[event_type][event].remove(handler_entry)

            if (len(self.handlers[event_type][event]) == 0):
               del(self.handlers[event_type][event])



   def handle_event(self, event_type, event, data, permissions=[]):
      """call all registered handlers for the event described by the arguments given."""
      #None is used as a wildcard for events.
      if (event_type in self.handlers):
         handler_entries = []
         #Test whether each handler-entry for this event_type matches this event.
         for element in self.handlers[event_type]:
            match = False
            if (element == True):
               #Entry True always matches.
               match = True

            elif (element == event):
               #Works potentially for arbitrary types and instances, though usually used for strings
               match = True
                              
            elif (hasattr(element, 'search')):
               #Mostly for regular expression objects, though any instance that includes
               #a method search which expects one string parameter can be used.
               try:
                  search_result = element.search(event)
               except StandardError:
                  self.logger.log(40, 'Exception while trying to search instance %s for event %s.' % (element, event), exc_info=True)

               else:
                  if (search_result != None):
                     match = True
                 
            if (match):
               handler_entries.extend(self.handlers[event_type][element])
         
         for handler_entry in handler_entries:
            sufficient_permissions = True
            for flag in handler_entry[1]:
               if not (flag in permissions):
                  sufficient_permissions = False

            if (sufficient_permissions):
               handler = handler_entry[0]
               try:
                  handler(self.parent, self.output, event_type, event, permissions, data)
               except StandardError:
                  self.logger.log(40, 'Exception in input handler:', exc_info=True)


class handlers_user:
   def handlers_modify(self, action, handler_types=None):
      if not (('handler_bindings' in dir(self)) and ('connections' in dir(self)) and (type(self.handler_bindings) == dict) and (type(self.connections) == dict)):
         raise StandardError('self.handler_bindings and/or self.connections does either not exist or is not a dictionary.')
      
      if (handler_types == None):
         handler_types = self.handler_bindings.keys()

      handlers_to_remove = []
      
      for handler_type in handler_types:
         if (handler_type in self.handler_bindings):
            handler_parent = self.connections[handler_type]
            if (handler_parent != None):
               handlers_to_remove = []
               for handler_entry in self.handler_bindings[handler_type]:
                  if (action == 'register'):
                     if (type(handler_entry) == dict):
                        handler_parent.handlers.add(**handler_entry)
                     else:
                        handler_parent.handlers.add(*handler_entry)
                  elif ((action == 'unregister') and not (handler_entry[2] in handlers_to_remove)):
                     handlers_to_remove.append(handler_entry[0])

               if (len(handlers_to_remove) > 0):
                  handler_parent.handlers.remove_all(handlers_to_remove)


class input_Option(optparse.Option):
   def take_action(self, action, dest, opt, value, values, parser):
      if action == "help":
         parser.print_help()
         raise ValueError('help requested')

      elif action == "version":
         parser.print_version()
         raise ValueError('version requested')

      else:
         optparse.Option.take_action(self=self, action=action, dest=dest, opt=opt, value=value, values=values, parser=parser)

class input_OptionContainer(optparse.OptionContainer):
   def format_option_help (self, formatter):
      if not self.option_list:
         return []
      result = []
      for option in self.option_list:
         if not option.help is optparse.SUPPRESS_HELP:
            result.extend(formatter.format_option(option))
      return result


class input_HelpFormatter(optparse.HelpFormatter):
   def format_option (self, option):
      lines = optparse.HelpFormatter.format_option(self, option).split('\n')
      return [line for line in lines if line]


class input_IndentedHelpFormatter(input_HelpFormatter):
    """Format help with indented section bodies."""

    def __init__(self, indent_increment=2, max_help_position=24, width=95, short_first=1):
        optparse.HelpFormatter.__init__(self, indent_increment, max_help_position, width, short_first)

    def format_usage(self, usage):
       return usage

    def format_heading(self, heading):
       return "%*s%s:" % (self.current_indent, "", heading)



class input_parser(input_OptionContainer, optparse.OptionParser):
   def __init__(self, custom_output, program_name='irc_interface', usage=None, option_list=None, option_class=input_Option, version=None, conflict_handler="error", description=None, formatter=input_IndentedHelpFormatter(), add_help_option=1, prog=None):
      optparse.OptionParser.__init__(self, usage=usage, option_list=option_list, option_class=option_class, version=version, conflict_handler=conflict_handler, description=description, formatter=formatter, add_help_option=add_help_option, prog=prog)
      self.custom_output = custom_output
      self.custom_program_name = program_name

   def error(self, msg):
      self.print_usage(None)
      self.custom_output(str(msg))
      raise ValueError(str(msg))

   def get_usage (self):
      if self.usage:
         return self.formatter.format_usage(self.usage.replace('%prog', self.custom_program_name))
      else:
         return ''

   def print_usage (self, file=None):
      if self.usage:
         self.custom_output(self.get_usage())

   def get_version(self):
      if self.version:
         return self.version
      else:
         return ''

   def print_version (self, file=None):
      if self.version:
         for line in self.get_version():
            self.custom_output(line)

   def print_help (self, file=None):
      for line in self.format_help():
         self.custom_output(line)

   def format_option_help (self, formatter=None):
      if formatter is None:
         formatter = self.formatter
      formatter.store_option_strings(self)
      result = []
      result.append(formatter.format_heading("options"))
      formatter.indent()
      if self.option_list:
         result.extend(input_OptionContainer.format_option_help(self, formatter))

      for group in self.option_groups:
         result.append(group.format_help(formatter))

      formatter.dedent()

      return result

   def format_help (self, formatter=None):
      if formatter is None:
         formatter = self.formatter
      result = []
      if self.usage:
         result.append(self.get_usage())
      if self.description:
         result.append(self.format_description(formatter))
      result.extend(self.format_option_help(formatter))
      return result


optparse.STD_HELP_OPTION = input_Option("-h", "--help", action="help", help="show this help message")

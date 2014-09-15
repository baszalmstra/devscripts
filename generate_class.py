#!/usr/bin/env python
import optparse
import re

class CppGeneratorIndenter():
  def __init__(self, generator, beginAdd = 1, endAdd = -1):
    self.generator = generator
    self.beginAdd = beginAdd
    self.endAdd = endAdd
  def __enter__(self):
    self.generator.indent(self.beginAdd)
  def __exit__(self, type, value, traceback):
    self.generator.indent(self.endAdd)

class CppGeneratorClass():
  def __init__(self, name, base, generator):
    self.name = name
    self.generator = generator
    self.base = base
  def __enter__(self):
    self.generator.line("class {0}{1}".format(self.name, (" : %s" % self.base) if self.base is not None else ""))
    self.generator.line("{")
    self.generator.indent(1)
  def __exit__(self, type, value, traceback):
    self.generator.indent(-1)
    self.generator.line("};")

class CppGenerator:
  def __init__(self, filename, tab = "  "):
    self.file = open(filename, "w")
    self.tab = tab
    self.indentationLevel = 0
  def indent(self, value):
    self.indentationLevel = self.indentationLevel + value
  def line(self, str):
    self.file.write((self.tab * self.indentationLevel) + str + "\n")
  def public(self):
    with CppGeneratorIndenter(self, -1, 1):
      self.line("public:")
    return CppGeneratorIndenter(self, 0,0)
  def classdef(self, name, base = None):
    return CppGeneratorClass(name, base, self)
  def commentline(self):
    return self.line("//" + ("-"*98))

def generateFileName(p, name):
  if p.library is not None:
    return "{0}/{1}.h".format(p.library, name)
  return "%s.h" % name
                        
def generateClassFilename(className):
  classNameWords = re.findall('[A-Z][^A-Z]*', className)
  return '_'.join([x.lower() for x in classNameWords])

def main():
  p = optparse.OptionParser(usage='usage: %prog [options] className')
  p.add_option('--namespace', '-n', default=None, help="Adds a namespace declaration to the source files")
  p.add_option('--library', '-l', default=None, help="Adds the library path before the include files")
  p.add_option('--precompiled', '-p', action="store_true", dest="precompiled", help="With this flag 'precompiled.h' is included before any other include file")
  p.add_option('--virtual', '-v', action="store_true", dest="virtual", help="Marks the descructor as virtual")
  p.add_option('--base', '-b', default=None, help="Name of the base class of the generated class")
  options, arguments = p.parse_args()
  if len(arguments) == 0:
    p.error("Must specify a className")
  
  className = arguments[0]
  classFileName = generateClassFilename(className)

  hpp = CppGenerator(classFileName + '.h')

  hpp.line("#pragma once")
  hpp.line("")
  
  if options.base is not None:
    hpp.line("#include \"%s\"" % generateFileName(options, generateClassFilename(options.base)))
    hpp.line("")
                        
  if options.namespace is not None:
    hpp.line("namespace %s {" % options.namespace)
    hpp.line("")
    hpp.indent(1)

  with hpp.classdef(className, options.base):
    with hpp.public():
      hpp.line("%s();" % className)
      hpp.line("{1}~{0}();".format(className, "virtual " if options.virtual else ""))

  if options.namespace is not None:
    hpp.indent(-1)
    hpp.line("}")

  cpp = CppGenerator(classFileName + '.cc')

  if options.precompiled:
    cpp.line("#include \"%s\"" % generateFileName(options, "precompiled"))

  cpp.line("#include \"%s\"" % generateFileName(options, classFileName))
  cpp.line("")

  if options.namespace is not None:
    cpp.line("namespace %s {" % options.namespace)
    cpp.line("")
    cpp.indent(1)

  cpp.commentline()
  cpp.line("{0}::{0}()".format(className))
  cpp.line("{")
  cpp.line("}");
  cpp.line("")

  cpp.commentline()
  cpp.line("{0}::~{0}()".format(className))
  cpp.line("{")
  cpp.line("}");

  if options.namespace is not None:
    cpp.indent(-1)
    cpp.line("}")

if __name__ == '__main__':
  main()
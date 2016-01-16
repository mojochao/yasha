"""
The MIT License (MIT)

Copyright (c) 2015-2016 Kim Blomqvist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from . import yasha

import os
from SCons.Builder import BuilderBase
from SCons.Scanner import Scanner
from SCons.Action import Action, CommandGeneratorAction

def is_c_file(file):
    suffix = os.path.splitext(str(file))[1]
    accept = [".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".s", ".S", ".asm"]
    return True if suffix in accept else False

class CBuilderBase(BuilderBase):
    def __call__(self, *args, **kw):
        """
        I would like to remove .h, .hh and .hpp files but then
        those aren't created at all. I'm confused cos I'm just
        removing those files from the output list of __call__()
        to avoid doing that extra step within SConstruct/Sconscript.
        """
        sources = BuilderBase.__call__(self, *args, **kw)
        return [x for x in sources if is_c_file(x)]

def CBuilder(action="yasha $SOURCE -o $TARGET"):
    """
    SCons builder for C
    """

    def source_scan(node, env, path):
        """
        TODO: Doesn't take custom parsers into account.
        """
        src = str(node.srcnode())
        src_dir = os.path.dirname(src)
        variant_dir = os.path.dirname(str(node))

        variable_formats = []
        for p in yasha.default_parsers():
            variable_formats += p.file_extension

        var = yasha.find_dependencies(src, variable_formats)
        ext = yasha.find_dependencies(src, [".py", ".j2ext", ".jinja-ext"])

        deps = [d for d in [var, ext] if d != None]
        deps = [d.replace(src_dir, variant_dir) for d in deps]
        return env.File(deps)

    def emit(target, source, env):
        env.Clean(target[0], str(target[0]) + ".d")
        return target, source

    def gtor(source, target, env, for_signature):
        cmd = ""
        if is_c_file(target[0]):
            cmd = action.replace("$SOURCE", str(source[0]))
            cmd = cmd.replace("$TARGET", str(target[0]))
        return cmd

    return CBuilderBase(
        action = CommandGeneratorAction(gtor, {}),
        #action = Action(action),
        emitter = emit,
        source_scanner = Scanner(function=source_scan),
        single_source = True
    )

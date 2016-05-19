#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#



import hashlib
import functools
import sys
import itertools
import os.path
import pickle
import inspect

import lib.graph.graph


class memorized(object):

    def __init__(self, memArgs=None):
        self.memArgs = memArgs
    # end def

    def __call__(self, func):
        self.func = func

        def mem_func(*args):
            return self.func(*args)  # Switch

            if self.memArgs:
                argnames = inspect.getargspec(self.func)[0]
                relargs = []
                for a, n in itertools.izip(args, argnames):
                    if n in self.memArgs:
                        relargs.append(a)
            else:
                relargs = args

            strargs = "(" + ", ".join(map(str, relargs)) + ")"
            hs = hashlib.md5(strargs).hexdigest()
            fn = 'memorized/' + self.func.__name__ + '/' + hs

            if os.path.isfile(fn):
                # print "read results of " + self.func.__name__ + strargs
                return self.read_result(fn, relargs)
            else:
                return self.save_result(fn, args, relargs)
        # end def
        return mem_func
    # end def

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def check_equal_args(self, arga, argb):
        if (len(arga) != len(argb)):
            return False

        for a, b in itertools.izip(arga, argb):
            t = type(a)
            if t != type(b):
                return False

            if t is graph.Graph:
                # if graph.graph_hash(a) != graph.graph_hash(b):
                #    return False
                return True
            elif t is graph.TFGraph:
                # if graph.graph_hash(a) != graph.graph_hash(b):
                #    return False
                return True
            else:
                if (a != b):
                    return False

        return True
    # end def

    def read_result(self, fn, relargs):
        fid = open(fn, "rb")
        value = pickle.load(fid)

        argif = pickle.load(fid)
        if not self.check_equal_args(relargs, argif):
            print "AAAHHHHH COLLISION!!!"
            sys.exit(1)

        return value
    # end def

    def save_result(self, fn, args, relargs):
        dn = os.path.dirname(fn)
        if not os.path.exists(dn):
            os.makedirs(dn)

        string = pickle.dumps(relargs)
        value = self.func(*args)

        fid = open(fn, "wb")

        pickle.dump(value, fid)  # write the value in the file
        fid.write(string)        # write the arguments in the file

        return value
    # end def
# end def

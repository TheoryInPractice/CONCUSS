#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import ConfigParser


def parse_config_safe(cfg_file):
    '''
    Wrapper that safely and graciously handles config files that don't exist
    '''
    parser = ConfigParser.ConfigParser()
    cfg_fp = open(cfg_file,'r')
    parser.readfp(cfg_fp)
    return parser

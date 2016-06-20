#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2016, gamesun
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of gamesun nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY GAMESUN "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL GAMESUN BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import re
g_match = re.compile('(?P<time>[0-9a-fA-F]{4}) (?P<value>[0-9a-fA-F]{4})')

def Parser(lines):
    """
    parser the data and display results at the canvas.
    Parser(list) -> [ duration,                            #info
                      [((x1,y1), (x2,y2), ... (xn,yn)),    #wave 1
                      (...),                               #wave 2
                      ...  ]]
    """

    RawData = [g_match.search(l) for l in lines]                                    # get the origin data
    lst = [[r.group('time'), r.group('value')] for r in RawData if r is not None]  # filter out the null data
    #lst.sort()
    for i in range(len(lst) - 1):
        if int(lst[i][0], 16) >= int(lst[i + 1][0], 16):
            for j in range(i + 1, len(lst)):
                lst[j][0] = hex(int(lst[j][0], 16) + 0xffff).split('x')[1]


    if 0 < len(lst):
#        matrix = [[(int(l[0], 16), int(v)) for v in bits(int(l[1], 16), 32)] for l in lst]
        matrix = [[(int(l[0], 16), (int(v) + 1) & 1) for v in bits(int(l[1], 16), 32)] for l in lst]
        matrix = zip(*matrix)           # zip(*matrix): Transpose the matrix
        zip_matrix = [[line[0],] + [p1 for p0, p1 in zip(line[0:], line[1:]) if p0[1] != p1[1]] + [line[-1],] for line in matrix[::-1]]
        full_matrix = [[line[0],] + [p1 for p0, p1 in zip(line[0:], line[1:])] + [line[-1],] for line in matrix[::-1]]
#        print matrix
        return (int(lst[-1][0], 16) - int(lst[0][0], 16), zip_matrix, full_matrix)
    return

def bits(data):
    while data:
        yield data & 1
        data >>= 1

def bits(data, bits):
    for i in xrange(bits):
        yield data & 1
        data >>= 1


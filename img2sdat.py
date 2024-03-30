#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ====================================================
#          FILE: img2sdat.py
#       AUTHORS: xpirt - luxi78 - howellzhu
#          DATE: 2018-05-25 12:19:12 CEST
# ====================================================

from __future__ import print_function

import os
import tempfile

import blockimgdiff
import sparse_img


def main(INPUT_IMAGE, OUTDIR='.', VERSION=None, PREFIX='system'):
    print('img2sdat binary - version: 1.7\n')
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    OUTDIR = OUTDIR + '/' + PREFIX
    blockimgdiff.BlockImageDiff(sparse_img.SparseImage(INPUT_IMAGE, tempfile.mkstemp()[1], '0'), None, VERSION).Compute(OUTDIR)
    print('Done! Output files: %s' % os.path.dirname(OUTDIR))

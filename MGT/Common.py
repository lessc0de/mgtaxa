### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the MGTAXA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##


from MGT.Util import *
from MGT.BatchRun import *
from MGT.Config import *
from MGT.UUID import *
from MGT.Debug import *

import numpy
import numpy.random as nrnd
n = numpy
nma = numpy.ma
from numpy import array
import random
from random import sample as sampleWOR #Random sampling w/o replacement
import os, sys, atexit, re, gzip
pjoin = os.path.join
from glob import iglob
import glob
import itertools
it = itertools
import operator
from types import StringTypes
from collections import defaultdict as defdict





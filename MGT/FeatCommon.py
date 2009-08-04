### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the MGTAXA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##


"""Common definitions used by feature-related modules"""
from MGT.Common import *

## Default Numpy dtype for class labels
labelDtype = n.dtype("f8")
## Default Numpy dtype for data split ids
splitDtype = n.dtype("i4")

## known formats of persistent storage of features
featIOFormats = ("txt","pkl")
## default value for format of persistent storage of features
defFeatIOFormat = "pkl"

class MGTSparseRealFeatures(object):
    """Datatype for sparse features of real numbers.
    Currently only used for Numpy datatype definitions,
    while the actual data is passed around as Numpy recarrays.
    @todo make it a subclass of numpy ndarray and hold the data here as well"""
    defDtype = n.dtype([("ind","i4"),("val","f4")])

class MGTSparseIntFeatures(object):
    """Datatype for sparse features of integer numbers.
    Currently only used for Numpy datatype definitions,
    while the actual data is passed around as Numpy recarrays.
    @todo make it a subclass of numpy ndarray and hold the data here as well"""
    defDtype = n.dtype([("ind","i4"),("val","i8")])


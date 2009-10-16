### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the MGTAXA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##


"""Some support for debugger. Tries to use IPython shell support if available"""
__all__ = ["pdb","set_trace"]
try:
    from IPython.Debugger import Pdb
    def set_trace():
        from IPython.Debugger import Pdb
        Pdb().set_trace()
    del Pdb
except:
    import pdb
    def set_trace():
        import pdb
        pdb.set_trace()
    del pdb
import pdb #legacy pdb.set_trace() use

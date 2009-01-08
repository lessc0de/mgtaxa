from MGT.Common import *

__all__ = ["App","runAppAsScript"]

class App:
    """Interface to application object. 
    The application can be started from shell scripts or called in-process from Python code.
    In both modes, it provides a method to schedule a batch queue execution."""

    ## Derived classes should set this to a list of opt.mode values that can result in submision of new batch jobs.
    batchDepModes = tuple()

    def __init__(self,args=[],opt=Struct()):
        """Constructor.
        @param args optional command line arguments to parse -
        if executing as a module, should pass None or sys.argv[1:], else - [], which should result in default values
        for all options.
        @param **opt keyword dict - values defined here will override those parsed from args.
        Two basic use patterns: 
        if running as a module:
            app = App(args=None)
            app.run()
        if calling from Python code:
            construct opt as a Struct() instance, specify only attributes with non-default values, then
            app = App(**opt)
            app.run()
        """
        optArgs, args = self.parseCmdLine(args=args)
        optArgs.updateOtherMissing(opt)
        if opt.optFile is not None:
            opt = loadObj(opt.optFile)
        self.opt = opt

    def run(self,**kw):
        """Run the application. 
        This is the method that is actually called by the user code. 
        Dispatches the work execution or batch submission depending on the options.
        @return list of sink BatchJob objects (if executed syncroniously, an empty list)"""
        opt = self.opt
        runMode = self.ajustRunMode(**kw)
        if runMode == "batch":
            return self.runBatch(**kw)
        elif runMode in ("inproc","batchDep"):
            curdir = os.getcwd()
            try:
                if "cwd" in kw:
                    os.chdir(kw["cwd"])
                ret = self.doWork(**kw)
            finally:
                if "cwd" in kw:
                    os.chdir(curdir)
            if ret is None:
                ret = []
            return ret
        else:
            raise ValueError(runMode)

    def ajustRunMode(self,**kw):
        opt = self.opt
        runMode = opt.runMode
        runMode = kw.get("runMode",runMode) #keyword overrides just for this instance
        if options.app.runMode not in ("default","batch","batchDep"):
            #we get infinite loop with any "batch*"
            runMode = options.app.runMode
        depend = kw.get("depend",None)
        if depend is not None and len(depend) > 0:
            #we can only run as "batch" or "batchDep" if we need to wait for dependency jobs
            #@todo make the current process to poll qstat at this location
            #if runMode is not "inproc".
            assert runMode in ("batch","batchDep")
        if runMode == "batchDep":
            if opt.mode not in self.batchDepModes:
                runMode = "batch"
        if hasattr(opt,"batchResume") and opt.batchResume:
            runMode = "inproc"
            opt.batchResume = False
        return runMode


    def doWork(self,**kw):
        """Do the actual work.
        Must be redefined in the derived classes.
        Private method. Should not be called directly by the user.
        Should work with empty keyword dict, using only self.opt.
        If doing batch submision of other App instances, must return a list of sink (final) BatchJob objects."""
        pass

    def runBatch(self,**kw):
        """Submit this application to run in batch mode.
        Can be redefined in derived classes.
        self.getCmdOptFile() will provide support for constructing the command line for batch script.
        BatchRun.runBatch() should be used to submit the batch job.
        We provide a generic implementation here that just submits itself with current options.
        Derived classes can define more complex schemes, e.g. fan out N parallel jobs plus
        one that starts on their completion to collect the results. 
        Although batch jobs can re-use runBatch() to submit other jobs, the return value of the top-most
        runBatch() will not know about these sub-jobs and therefore could not define dependencies on them.
        The requirement to this method is that it must have a quick running top-level mode suitable
        to call on the login host.
        It can be called from both self.run() when 'batch' option is set, and directly from external code.
        @ret list of BatchJob objects corresponding to the sinks (final vertices) in the DAG of submitted jobs.
        If kw["runMode"] or global options.app.runMode == "inproc" it will call self.run() instead of submitting a batch job."""
        opt = copy(self.opt)
        if opt.runMode == "batch":
            opt.runMode = "inproc" #avoid infinite loop
        opt.batchResume = True
        opt.optFile = None
        kw = kw.copy()
        kw.setdefault("scriptName",self.getAppName())
        dryRun = kw.get("dryRun",False)
        cmd = self.getCmdOptFile(**kw)
        if not dryRun:
            dumpObj(opt,cmd.optFile)
        else:
            print "opt = \n", opt
        return [ runBatch(cmd.cmd,dryRun=dryRun,**kw) ]

    @classmethod
    def parseCmdLine(klass,args=None):
        """Obtain options from command line arguments.
        It is called from constructor or directly by the user.
        Derived classes must redefine makeOptionParserArgs() and optionally parseCmdLinePost() 
        if they need to parse additional arguments.
        The arguments defined here are needed by the App infrastructure: 
        --opt-file -> optFile (None); --batch -> batch (False).
        When called directly from the user code, the args is typically set to [] in order to obtain
        the default values for all options. Thus, it is important the the implementation provides
        reasonable defaults in a context independent way (e.g. without including the current directory info).
        @param args command line arguments (pass [] to get default values, pass None to use sys.argv[1:])"""
        from optparse import OptionParser, make_option
        option_list = [
            make_option(None, "--opt-file",
            action="store", type="string",dest="optFile",default=None,
            help="Load all program otions from this pickled file"),
            make_option(None, "--run-mode",
            action="store", type="choice",choices=("batch","inproc"),dest="runMode",default="inproc",
            help="Choose to batch-run or in-process"),
        ]
        parseArgs = klass.makeOptionParserArgs()
        parseArgs.option_list.extend(option_list)
        parser = OptionParser(**parseArgs.asDict())
        (options, args) = parser.parse_args(args=args) #values=opt does not work
        options = Struct(options.__dict__)
        klass.parseCmdLinePost(options=options,args=args,parser=parser)
        return options,args

    @classmethod
    def makeOptionParserArgs(klass):
        """Return a Struct with optparse.OptionParser constructor arguments specific to the application.
        The "option_list" attribute must be obtained with a sequence of calls to optparse.make_option.
        Other possible attributes can be e.g. "usage".
        This method will be called by parseCmdLine() and the returned "option_list" concatenated with the default
        one provided by the parseCmdLine().
        Must be redefined in the derived class only if there are any application specific command-line options."""
        return Struct(usage="%prog [options]",option_list=[])

    @classmethod
    def parseCmdLinePost(klass,options,args,parser):
        """Optionally modify options and args in-place.
        Called at the end of parseCmdLine to allow the derived classes customizing the option processing.
        @param options options returned by OptionParser and converted to Struct object
        @param args args returned by OptionParser
        @param parser OptionParser object used to parse the command line - needed here to call its error() method
        if necessary.
        options should be modified in place by this method"""
        pass

    @classmethod
    def defaultOptions(klass):
        return klass.parseCmdLine(args=[])


    def getAppName(self):
        """Return mnemonic name for this application to use for example as a prefix of batch script name"""
        s = self.__class__.__name__
        return s[0].lower()+s[1:]

    def factory(self,**kw):
        """A factory function (class constructor by default) that creates a new instance of self.
        This is needed when the application needs to batch-submit a new instance of itself."""
        return self.__class__(**kw)

    def getCmd(self):
        """Return command line that starts this application from shell, w/o options.
        python -m runpy mechanism is used if we can get the module name of self (Python 2.5 is required),
        and python sys.argv[0] otherwise.
        This is dependent on our requirement that the App derived class is located inside the module
        with the same name as class name, and the proper start-up code is present at the module level."""
        import inspect
        modname = inspect.getmodule(self).__name__
        if modname == "__main__":
            #executed as script, module name is not available but we can execute the same way again
            return "python " + sys.argv[0]
        else:
            #__name__ has a full import path and we can use runpy mechanism
            return "python -m runpy " + modname

    def getCmdOptFile(self,cwd=os.getcwd(),**kw):
        """Generate unique file name for a new options pickle file and build full command line with it.
        @param cwd optional directory for the new file (current dir by default)
        @ret Struct(optFile,cmd) where optFile is file name, cmd is command line, 
        such as self.getCmd()+' --opt-file '+optFile."""
        out,optFile = makeTmpFile(suffix=".opt.pkl",prefix=self.getAppName()+'.',dir=cwd)
        out.close()
        return Struct(optFile=optFile,cmd=self.getCmd() + " --opt-file %s" % optFile)

def runAppAsScript(klass):
    app = klass(args=None)
    return app.run()

## This is an example of the code that must be in every module with a class derived from App.
## App class must be correspondingly replaced with derived class.

if __name__ == "__main__":
    runAppAsScript(App)

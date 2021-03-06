### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the MGTAXA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##


"""Support for running jobs in a batch environment."""
from MGT.Util import *
from MGT.Config import *
from MGT.BatchMakeflow import *

class BatchJob(Struct):
    """Description of submitted job"""
    pass

_BatchJobTemplateBash = \
"""#!/bin/bash
#$$ -cwd
#$$ -r n
${lrmSiteOptions}
${lrmUserOptions}
## Submit as 'qsub -b n -S /bin/bash script_name'. Apparently admins changed the default value of -b to 'y'
## and by default qstat now thinks of script_name as a binary file and does not parse it for
## embedded options (09/14/07).  Shell NEEDS to be correctly specified both at the top and (?) 
## in qsub options for the user environment to be correctly sourced.

batchHostDebug=${batchHostDebug}

if [ -n "$$batchHostDebug" ]; then
    echo "######### Initial environment begin"
    printenv | sort
    echo "######### Initial environment end"
    ## pstree
    ## Sourcing .bashrc is not enough - only .profile creates MACHTYPE, on which .environ depends
fi

source ~/.profile

${envRc}

if [ -n "$$batchHostDebug" ]; then
    echo "########## Execution environment begin"
    printenv | sort
    echo "########## Execution environment end"
    hostname
    uname -a
    pwd
    date
    top -b -n 1 | head -n 15
    ####
fi
set -e
"""
_BatchJobTemplate = _BatchJobTemplateBash

class BatchSubmitter(object):

    qsubOptsDelim = r"#$ "
    
    @classmethod
    def defaultOptions(klass):
        opts = Struct()
        # use global options
        if hasattr(options,"batchRun"):
            options.batchRun.updateOtherMissing(opts)
        opts.setdefault('lrmSiteOptions',r'')
        opts.setdefault('lrmUserOptions',None)
        opts.setdefault("stdout",None)
        opts.setdefault("stderr",None)
        opts.setdefault("batchHostDebug","") #should be empty for all web jobs
        opts.setdefault("batchBackend","qsub")
        return opts
    
    def __init__(self,**kw):
        opts = self.defaultOptions()
        self.opts = opts
        opts.updateFromDefinedOtherExisting(kw)
        if opts.envRc is None:
            opts.envRc = ""
        else:
            opts.envRc = "source %s" % (opts.envRc,)
        opts.setIfUndef("lrmUserOptions","")
        if opts.stdout is not None:
            opts.lrmUserOptions += " -o %s" % (opts.stdout,)
        if opts.stderr is not None:
            opts.lrmUserOptions += " -e %s" % (opts.stderr,)
        if opts.lrmUserOptions:
            opts.lrmUserOptions = "%s %s" % (self.qsubOptsDelim,opts.lrmUserOptions)
        if opts.lrmSiteOptions:
            opts.lrmSiteOptions = "%s %s" % (self.qsubOptsDelim,opts.lrmSiteOptions)
        self.header = varsub(_BatchJobTemplate,**opts.asDict())
        
    def submit(self,cmd,scriptName=None,cwd=None,sleepTime=0,depend=[],dryRun=False):
        """Submit a batch job.
        @param cmd Command to run - it will be inserted verbatim into a script submitted to qsub
        @param scriptName Optional prefix for batch script name
        @param cwd Optional execution directory, otherwise the current directory will be used
        @param sleepTime sleep that many seconds after submission
        @param depend list of either job IDs or BatchJob instances on which completion the current job depends upon
        @param dryRun if True, just print what would have been done, without submitting anything
        @ret BatchJob instance for submitted job"""
        opts = self.opts
        ret = None
        curdir = os.getcwd()
        try:
            if cwd:
                os.chdir(cwd)
                #convert cwd to abspath
                cwd = os.getcwd()
            else:
                cwd = curdir
            if scriptName is None:
                scriptName = osNameFilter(cmd)[:10]
                if scriptName == "":
                    scriptName = "bs"
            outScr,scriptName = makeTmpFile(suffix=".qsub",prefix=scriptName+'.',dir=cwd,withTime=True)
            outScr.close()
            flagOk = scriptName+".flag_ok"
            script = """\
            %s
            cd %s
            rm -f %s
            %s
            echo "OK" > %s
            """ % (self.header,cwd,flagOk,cmd,flagOk)
            strToFile(script,scriptName,dryRun=dryRun)
            if opts.batchBackend == "qsub":
                qsubCmd = ["qsub", "-b","n","-S","/bin/bash"]
                #construct dependency argument if needed
                if len(depend) > 0:
                    depids = []
                    for dep in depend:
                        if isinstance(dep,BatchJob):
                            depid = dep.jobId
                        elif isinstance(dep,str):
                            depid = dep
                        else:
                            raise ValueError("'depend' should be a flat list of scalar types. Perhaps you used jobs.append(app.run()) instead of jobs.extend(app.run()) when build the jobs list")
                        depids.append(depid)
                    qsubCmd.extend(["-hold_jid",','.join(depids)])
                qsubCmd.append(scriptName)
                
                nToTry = 3

                while True:
                    try:
                        outp = backsticks(qsubCmd,dryRun=dryRun,dryRet="your job 0 ")
                    except CalledProcessError,msg:
                        nToTry -= 1
                        if nToTry > 0:
                            print "Warning: qsub returned error code, trying %s more times: %s" % (nToTry,msg)
                        else:
                            raise
                    else:
                        break

                jobId = outp.lower().split("your job")[1].strip().split()[0]
                strToFile(jobId,scriptName+".jobid",dryRun=dryRun)
                if not dryRun:
                    # go easy on qsub subsystem
                    sleep(sleepTime)
            elif opts.batchBackend == "makeflow":
                jobId = scriptName
            else:
                raise ValueError("Unknown value of batchBackend: %s" % (opts.batchBackend,))
            ret = BatchJob(jobId=jobId,scriptName=scriptName,cwd=cwd,outputs=(flagOk,),depend=depend)
        finally:
            os.chdir(curdir)
        return ret
        
    def nQueued(self):
        jobList = backsticks(["qstat","-u",os.environ['USER']]).strip().splitlines()
        return len(jobList)

    def submitIf(self,maxQueued,**kw):
        while self.nQueued() >= maxQueued:
            sleep(60)
        self.submit(**kw)

def runBatch(cmd,scriptName=None,cwd=None,sleepTime=0,depend=[],dryRun=False,**kw):
    if not isinstance(cmd,str):
        cmd = ' '.join(cmd)
    bs = BatchSubmitter(**kw)
    return bs.submit(cmd=cmd,scriptName=scriptName,cwd=cwd,sleepTime=sleepTime,depend=depend,dryRun=dryRun)


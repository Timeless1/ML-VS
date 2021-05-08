import time
import os,subprocess,sys,re,shutil,traceback
import errno,pickle

start = time.clock()
def runSaveSubprocess(cmdline='',outPrefix='out'):
    # cmdline = "python ../../../CYS_cavity_grep_single.py --pdbID %s --residue %s"%(pdbID,"CYS")
    if cmdline=='':
        raise AssertionError("cmdline could not be empty.")
        
    # stdout & stderr are saved in to files to avoid deadlock
    outname = "%s.out"%(outPrefix)
    errname = "%s.err"%(outPrefix)
    fh1 = open(outname,'w')
    fh2 = open(errname,'w')
    print(cmdline)
    subprocess.Popen(cmdline,shell=True,stdout=fh1,stderr=fh2).wait()
    fh1.flush()
    fh2.flush()
    os.fsync(fh1)
    os.fsync(fh2)
        #time.sleep(1)
    fh1.close()
    fh2.close()
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def rdock_single(batch):
    #print("%s is submitted"%(batch))
    
    #workDir = os.path.dirname(batch)

    #print(workDir)
    #topDir = os.getcwd()
    #workDir = os.path.join(topDir,batch)
    
    #mkdir_p(workDir)
    #mkdir_p(batch)
    #os.chdir(workDir)
    
    #size = 1
    #start = (int(batch)-1)*size+1
    #stop = start+size-1

    #cmdline = 'echo "rbdock -r hivpr_rdock.prm -p dock.prm -n 50 -i compound/sdf_%03d.sdf -o result_%03d"'%(batch,batch)
    #print(cmdline)
    
    #cmdline = 'rbdock -r protein_rdock.prm -p dock.prm -n 2 -i compound/sdf_%03d.sdf -o result_%03d'%(batch,batch)
    cmdline = 'rbdock -r ../confile/protein.prm -p dock.prm -n 20 -i ../outputfile/%d.sd -o ../outputfile/result_%d'%(batch,batch)
    runSaveSubprocess(cmdline,'../outputfile/log_%d'%(batch))
    


    # cmdline = "sdsort -n -f'SCORE' -s result_%d.sd > sorted-%d.sd"%(batch,batch)
    # runSaveSubprocess(cmdline,'log_sort_%03d'%(batch))
    
    # cmdline = "sdFirstPose -f'ddd' sorted-%03d.sd > sorted-first-%03d.sd"%(batch,batch)
    # runSaveSubprocess(cmdline,'log_sort_first_%03d'%(batch))
    
    #os.chdir(topDir)
    #time.sleep(20)


   


#numbers = ['01','02','03','04','05','06']
numbers = [i for i in range(1,31)]
from concurrent import futures
if __name__=='__main__':
    with futures.ProcessPoolExecutor(max_workers=30) as executor:
        jobs = []
        for batch in numbers:
            time.sleep(2)
            job = executor.submit(rdock_single,batch)
            jobs.append(job)

        for job in futures.as_completed(jobs):
            print(job)
            print(job.result())
            

Time_cost = (time.clock() - start)
print(Time_cost)
# if __name__ == '__main__':
#     sum = 0
#     for i in range(20):
#         start = time.time()
#         pool = ProcessPoolExecutor(max_workers=4)
#         results = list(pool.map(gcd, numbers))
#         end = time.time()
#         sum += end - start
#     print("ProcessPool concurrent")
#     print(sum/60)               # 0.8655495047569275

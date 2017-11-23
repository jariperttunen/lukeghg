import grp
import pwd
import os
import glob
import time

def FileOwner(dirfilels):
    dictionary={}
    for filename in dirfilels:
        stat_info = os.stat(filename)
        st_uid = stat_info.st_uid
        st_gid = stat_info.st_gid
        tmod = os.path.getmtime(filename)
        ltime = time.localtime(tmod) 
        ltimestr = str(ltime[0])+":"+str(ltime[1])+":"+str(ltime[2])+":"+str(ltime[3])+":"+str(ltime[4])
        user=""
        try:
            user = pwd.getpwuid(st_uid)[0]
        except KeyError:
            user=st_uid
        #group = grp.getgrgid(gid)[0]
        try:
            f = open(filename,'r')
            ls = [x.rpartition('#')[2].split() for x in f.readlines() if x.count('#') != 1] 
            for x in ls:
                #possibly an empty line at the end of file
                if len(x) > 0:
                    uid = x.pop(0)
                    uid_new = uid.strip('{}')
                    dictionary[uid_new] = (os.path.basename(filename),ltimestr,user)
        except IOError:
            print("Cannot open file:",filename)
    return dictionary

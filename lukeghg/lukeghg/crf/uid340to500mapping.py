def MapUID340to500(uid,uid340set,uiddict340to500):
    """Check if the UID is in the changed uid set (uid340set).
       If so, map the uid to new one
    """
    if uid in uid340set:
        uid = uiddict340to500[uid]
    return uid

def Create340to500UIDMapping(uid_mapping_file):
    """Create UID mapping from CRFReporter 3.4.0 to 5.0.0.
       Some UIDs have changed in LULUCF.
    """
    uid340set=set()
    uiddict340to500={}
    f = open(uid_mapping_file)
    for line in f:
        #Strip white space and newline
        line=line.strip(' \n')
        uidls=line.split(',')
        uid340set.add(uidls[0])
        uiddict340to500[uidls[0]]=uidls[1]
    return (uid340set,uiddict340to500)

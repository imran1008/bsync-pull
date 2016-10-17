#!/bin/python3

import config
import datetime
import fcntl
import optparse
import os
import subprocess
import sys

def subprocessCall(args, dry_run, ok_if_fail=False):
    print(' '.join(args))

    if not dry_run:
        assert subprocess.call(args) == 0 or ok_if_fail, "Child process failed"

def remoteBtrfsSubvolume(host, args, dry_run, ok_if_fail=False):
    fullArgs = ['ssh', host, 'sudo', 'btrfs', 'subvolume']
    fullArgs.extend(args)
    subprocessCall(fullArgs, dry_run, ok_if_fail=ok_if_fail)

def createSnapshot(profile, dest, dry_run):
    host = profile['hostname']
    src = profile['source']

    print("Syncing remote filesystem")
    subprocessCall(['ssh', host, 'sync'], dry_run)

    print("Creating a remote snapshot")
    remoteBtrfsSubvolume(host, ['snapshot', '-r', src, dest], dry_run)

def deleteRemoteSnapshot(host, subvolume, dry_run):
    remoteBtrfsSubvolume(host, ['delete', subvolume], dry_run, ok_if_fail=True)

def downloadSnapshot(host, new_src, dest, dry_run):
    if not os.path.exists(dest):
        os.mkdir(dest)

    subprocessCall(['buttersink', 'ssh://' + host + new_src, dest], dry_run)

def deleteLocalSnapshot(subvolume, dry_run):
    subprocessCall(['btrfs', 'subvolume', 'delete', subvolume], dry_run, ok_if_fail=True)

def getCounter(filename):
    counter = 0
    if os.path.isfile(filename):
        handle = open(filename)

        for i, l in enumerate(handle):
            pass

        counter = i + 1
        handle.close()

    return counter

def getRemoteSnapshotPath(profile, counter):
    prefix = profile['snapshot_dir'] + '/' + profile['snapshot_name']

    snapshot = {}
    snapshot['old'] = None
    if counter != 0:
        snapshot['old'] = prefix + str(counter)

    snapshot['new'] = prefix + str(counter + 1)
    return snapshot

def getLocalSnapshotPath(profile, counter):
    dest = profile['destination']

    snapshot = {}
    snapshot['old'] = None
    if counter > profile['num_snapshots']:
        old_idx = counter - profile['num_snapshots'] + 1
        snapshot['old'] = dest + '/' + profile['snapshot_name'] + str(old_idx)

    snapshot['new'] = dest + '/.'
    return snapshot

def lockFile(lockfile):
    fp = open(lockfile, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False

    return True

def main():
    usage = "usage: " + sys.argv[0] + " [options] <profile name>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-d", "--dryrun",
		      action="store_true", dest="dryrun", default=False,
		      help="enable dry-run mode")

    (options, args) = parser.parse_args()

    # get profile name
    if len(args) < 1:
        print(usage)
        exit(1)

    profile_name = args[0]

    # get commandline options
    dry_run = options.dryrun
    profile = config.profiles[profile_name]

    # create the lock file
    if not lockFile(profile['lock_file']):
        print("profile " + profile_name + " is locked")
        exit(0)


    # get the backup count number
    state_filename = profile['state_file']
    counter = getCounter(state_filename)
    print("Current backup count: " + str(counter+1))

    # get snapshot paths
    remote_snapshot = getRemoteSnapshotPath(profile, counter)
    local_snapshot = getLocalSnapshotPath(profile, counter)

    # create a new snapshot.
    start_time = datetime.datetime.now().isoformat()
    createSnapshot(profile, remote_snapshot['new'], dry_run)

    # download the snapshot.
    host = profile['hostname']
    downloadSnapshot(host,
                     remote_snapshot['new'],
                     local_snapshot['new'],
                     dry_run)

    # delete remote snapshot from the source machine that is one-step older
    # than the one that was just created.  the snapshot that was just created
    # above will serve as the base for the next buttersink.
    if remote_snapshot['old'] != None:
        deleteRemoteSnapshot(host, remote_snapshot['old'], dry_run)

    # delete local snapshot that is a few backups old
    if local_snapshot['old'] != None:
        deleteLocalSnapshot(local_snapshot['old'], dry_run)

    end_time = datetime.datetime.now().isoformat()

    # append the current timestamp to the state file
    if not dry_run:
        handle = open(state_filename, 'a')
        handle.write(str(counter) + '\t' + start_time + '\t' + end_time + '\n')
        handle.close()

if __name__ == "__main__":
    main()



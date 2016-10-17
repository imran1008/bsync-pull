#!/bin/python

profiles = {
    'example': {
        # hostname of the source machine. if the login user name is the same
        # as the current user name, the 'user@' part can be left out
        'hostname': 'user@example.com',

        # number of recent snapshots to keep. the rest will be deleted
        'num_snapshots': 4,

        # snapshot name prefix. the snapshot counter will be appended to this
        # prefix everytime a new snapshot is taken
        'snapshot_name': 'backup',

        # location of the state file. this file will contain the snapshot
        # number along with the begin/end time of the backup process
        'state_file': '/var/local/bsync-pull-example',

	# location of the lock file.  this file ensures that only one instance
        # of the profile is running.  it's valid to specify the same lock file
        # for multiple profiles.  doing so will also ensure that no two
        # profiles with the same lock file are running at the same time.
        'lock_file': '/var/local/bsync-pull-lock',

        # path in the destination machine (localhost) where the snapshots
        # will be saved. this path should NOT end with a '/'. the final path
        # will be $destination/$snapshot_name$counter
        'destination': '/subvolumes/remote/storage0',

        # path in the source machine (remote) of the subvolume that is to
        # be backed up
        'source': '/mnt/storage0',

        # path in the source machine (remote) of the directory where the
        # last snapshot will be stored. this directory must be within the
        # same btrfs filesystem as the source subvolume.
        #
        # only one snapshot will be kept in this directory. this snapshot
        # serves as the reference point when the next backup is performed.
        'snapshot_dir': '/mnt/storage0/subvolumes'
    }
}



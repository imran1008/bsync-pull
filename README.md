# About
bsync-pull is a backup utility for use with btrfs filesystems. This utility
uses a pull model for its backup process as opposed to a more traditional push
model. Details about the design decisions are explained below.

# Design
Most backup utilities available today run on the primary machine and
periodically pushes the data from the primary machine to the backup machine.
The advantage of this approach is that the backup machine can be treated as a
very simple data store.

The problem with this push model is that the primary machine periodically
mounts the backup machine with read-write access. If the primary machine is
ever compromised, the attacker can destroy all backups as well since the
primary machine as write access to the backup machine.

When operating a backup system with a pull model, the utility runs on the
backup machine and periodically pulls data from the primary machine. In this
model, the primary machine needn't have any access to the backup machine and
the backup machine has restricted write access to the primary machine.

# Dependencies
The following is a list of dependencies for bsync-pull

 - [Btrfs progs](https://btrfs.wiki.kernel.org/index.php/Btrfs_source_repositories)
 - [ButterSink](https://github.com/AmesCornish/buttersink)
 - [OpenSSH](http://www.openssh.com)
 - [Python 3](https://www.python.org)
 - [sudo](https://www.sudo.ws)

# Usage
The config.py script contains a list of profiles for use with the utility. It
comes with an example profile with documented comments for each field.

To run the tool, simply execute the following command

    bsync-pull.py <profile name>

You can optionally add the --dryrun to see the commands without actually
executing them.



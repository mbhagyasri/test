#!/bin/bash
# db-backup - full online PostgreSQL database backup
#set -x

DBUSER=postgres
BASEDIR=/var/backup/base
LOGSDIR=/var/backup/logs
BKEEPDIR=/var/backup/retain
TSTAMP=$(date "+%Y%m%d-%H%M%S")
BKEEPDAYS=7

# Compute free space (for non-root user) in MB
# Directory passed as argument, result returned on stdout

fsfreemb() {
  local FREEBLKS BLKSIZE
  eval $(stat -f -c "FREEBLKS=%a BLKSIZE=%S" $1)
  local FREEMB=$(($FREEBLKS * $BLKSIZE / 1024 / 1024))
  echo $FREEMB
}

# Refuse to proceed if environment is not sane
if [[ $USER == "" ]] ; then
    USER=$(whoami)
fi

if [[ ! -d $BASEDIR ]] ; then
  echo "Base backup directory $BASEDIR does not exist!" 1>&2
  exit 1
elif [[ ! -d $LOGSDIR ]] ; then
  echo "WAL archive directory $LOGSDIR does not exist!" 1>&2
  exit 1
elif [[ $USER == root ]] ; then
  CMDRUN='su - '"$DBUSER"' -c "pg_basebackup -D '"$BASEDIR"' -Ft -z"'
elif [[ $USER == $DBUSER ]] ; then
  CMDRUN="pg_basebackup -D $BASEDIR -Ft -z"
else
  echo "This script must be executed by root or $DBUSER!" 1>&2
  exit 2
fi

# Step 0. (left as exercise for the student) While not required, it is
# highly desireable for previous backup output to have been saved (by BUaaS)
# so that we have a fallback for the case where the backup we are about to
# run next fails (or subsequently is corrupted and unrecoverable). There is
# no mechanism at present to trigger an external backup to ensure this is
# in fact the case, so do nothing.

# Step 1. The destination directory for the backup must be empty.

echo "`date` Cleaning base backup directory ..."
BEFORE=$(fsfreemb $BASEDIR)
find $BASEDIR -type f -delete
AFTER=$(fsfreemb $BASEDIR)
echo "$BEFORE MB available before cleanup, $AFTER MB available now"

# Step 2. Create the base backup.

echo "`date` Starting PostgreSQL base backup ..."
cd /tmp # Avoid sudo complaints

eval $CMDRUN
#$CMDPREFIX "pg_basebackup -D $BASEDIR -Ft -z"

RC=$?
if [[ $RC == 0 ]] ; then
    if [[ ! -d ${BKEEPDIR} ]] ; then
       mkdir ${BKEEPDIR}
       chown 999 ${BKEEPDIR}
    fi
    cp $BASEDIR/base.tar.gz $BKEEPDIR/base-${TSTAMP}.tar.gz
    cp $BASEDIR/pg_wal.tar.gz $BKEEPDIR/pg_wal-${TSTAMP}.tar.gz
fi

echo "`date` Backup completed with status $RC"
FINAL=$(fsfreemb $BASEDIR)
echo "$FINAL MB remaining in filesystem"

# Step 3. Most of the archived WAL logs (which predate the full backup)
# no longer are required and can/should be deleted. The base backup
# created a marker file (xxxxxxxxxxxxx.yyyyyyyyyy.backup) indicating the
# earliest WAL log (xxxxxxxxxxxxx) required to restore this backup; all
# earlier WAL logs can safely be deleted.

echo "`date` Cleaning unnecessary archived WAL files ..."
KEEP=0
PURGE=0
STATE=0

# Naming convention ensures sort order == chronological order. Process in
# reverse order; once we pass the designated marker, everything can be
# deleted.

BEFORE=$(fsfreemb $LOGSDIR)
cd $LOGSDIR
for FILE in `ls -1r` ; do
  case $STATE in
    0) # Scanning for marker
      KEEP=$(($KEEP + 1))
      if [[ $FILE =~ .*\.backup ]] ; then
        STATE=1 # Marker found, transition to next state
        CUTOFF=${FILE%%.*.backup} # First (oldest) required WAL
        echo "WAL archives older than $CUTOFF will be deleted"
      fi
      ;;
    1) # Scanning for cutoff file (which should appear immediately)
      KEEP=$(($KEEP + 1))
      if [[ $FILE == $CUTOFF ]] ; then
        STATE=2 # Cutoff passed, transition to next state
      fi
      ;;
    2) # Deleting unwanted files
      PURGE=$(($PURGE + 1))
      rm -f $FILE
      ;;
  esac
done
AFTER=$(fsfreemb $LOGSDIR)

echo "`date` Removed $PURGE files, retained $KEEP files"
echo "$BEFORE MB available before cleanup, $AFTER MB available now"

# Step 4: purge longer term retention directory BKEEPDIR
#
if [[ $RC == 0 ]] ; then
    find ${BKEEPDIR}/* -mtime +${BKEEPDAYS} -exec rm -rf {} \;
fi

exit $RC

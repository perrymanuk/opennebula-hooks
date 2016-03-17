#!/bin/bash
id=$1
template=$2
userid=`onevm show -x $1 | grep UID | sed 's/<UID>//g' | sed 's/<\/UID>//g'`

groupid=`oneuser show -x $userid | grep GID | sed 's/<GID>//g' | sed 's/<\/GID>//g'`
groupshare=`onegroup show -x $groupid | grep GROUPSHAREPERMS | sed 's/<GROUPSHAREPERMS>//g' | sed 's/<\/GROUPSHAREPERMS//g'`
if [[ $groupshare == *'4'* ]] ; then
    echo $groupshare
    onevm chmod $id 640;

elif [[ $groupshare == *'6'* ]] ; then
    echo $groupshare
    onevm chmod $id 660;
elif [[ $groupshare == *'1'* ]] ; then
    echo $groupshare
    onevm chmod $id 610;
elif [[ $groupshare == *'2'* ]] ; then
    echo $groupshare
    onevm chmod $id 620;
elif [[ $groupshare == *'5'* ]] ; then
    echo $groupshare
    onevm chmod $id 650;
elif [[ $groupshare == *'7'* ]] ; then
    echo $groupshare
    onevm chmod $id 670;
fi



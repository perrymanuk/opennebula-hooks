#!/bin/bash
VMID=$1
TEMPLATE=$2
DCTEMP=`echo $TEMPLATE | base64 --decode`
echo $DCTEMP > /tmp/doneDCTEMP$VMID
logger "ONEHOOK - VM:$VMID - Aquilon Reset"

kinit -k HTTP/<hostname>

IPADDRESS=`xpath /tmp/doneDCTEMP$VMID "VM/TEMPLATE/NIC/IP/text()"`
aqhost=`curl -s http://aquilon.gridpp.rl.ac.uk:6901/find/host?ip=$IPADDRESS`
echo "$aqhost,$IPADDRESS" > /tmp/aq-hostname

curl_cmd='/usr/bin/curl -s --negotiate -u : --capath /etc/grid-security/certificates/ -XPOST'
url_prefix='https://aquilon.gridpp.rl.ac.uk/private/aqd.cgi'

domain='domain'
counter=0
while  [[ $domain != *"No data"* ]] && [[ $domain != "" ]]  && [ $counter -lt 5 ];
do
   domain=`$curl_cmd "$url_prefix/command/manage_hostname?hostname=$aqhost&domain=prod&force=true"`
   counter=$((counter+1))
   if [[ $domain == *"No data"* ]] || [[ $domain == "" ]];
   then
       kinit -k HTTP/<hostname>
   fi
done
if [ $counter -eq 5 ] ;
then
    logger "ONEHOOK - VM:$VMID - AQ Reset - AQ Domain Failed"
else
    logger "ONEHOOK - VM:$VMID - AQ Reset - AQ Domain Assigned"
fi

echo $domain >> /tmp/aq-hostname
personality='personality'
counter=0
while [[ $personality != *"No data"* ]] && [[ $personality != "" ]] && [ $counter -lt 5 ] ;
do
    personality=`$curl_cmd "$url_prefix/host/$aqhost/command/make?personality=nubesvms&osversion=6x-x86_64&archetype=ral-tier1&osname=sl"`
    counter=$((counter+1))
    if [[ $personality == *"No data"* ]] || [[ $personality == "" ]];
    then
        kinit -k HTTP/<hostname>
    fi

done
if [ $counter -eq 5 ] ;
then
    logger "ONEHOOK - VM:$VMID - AQ Reset - AQ Personality&OS Failed"
else
    logger "ONEHOOK - VM:$VMID - AQ Reset - AQ Personality&OS Assigned"
fi
echo $personality >> /tmp/aq-hostname

#if [[ $domain != *' '* ]]
#then
#    failure='yes'
#    domainmessage="Failed to change"
#else
#    domainmessage="Succeeded"
#fi
if [[ $domain$personality == *'500'* ]]
then
    failure='yes'
    logger "ONEHOOK - VM:$VMID - Failed to Reset"
    persmessage="Failed to change"
else
    persmessage="Succeeded"
fi
if [[ $failure == 'yes' ]]
then
 mail -s "Error resetting $aqhost" "<emailaddress>"<<EOF
Error resetting $aqhost
Personality
$persmessage

Domain
$domain

Personality
$personality
EOF

else
logger "ONEHOOK - VM:$VMID - Reset Succeeded"
fi
rm /tmp/doneDCTEMP$VMID -f

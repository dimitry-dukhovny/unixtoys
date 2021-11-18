#!/bin/bash

# Configure this part
mydaemon=squid

# Derived, but also configurable
outfile=/tmp/check.${mydaemon}
pidfile=/var/run/${mydaemon}.pid

# Bookkeeping
mypid=$$
myname=$0
mydir=`dirname ${myname}`

# Import node-specific configuration
if [ ! -f ${mydir}/check.config.sh ]
then
    echo ${mydir}/check.config.sh is missing.  I am lost.
    exit 255
fi
. ${mydir}/check.config.sh

# Import common functions after declaring configuration
if [ ! -f ${mydir}/check.functions.sh ]
then
    echo ${mydir}/check.functions.sh is missing.  I am lost.
    exit 255
fi
. ${mydir}/check.functions.sh


#httpdcount=`ps -ef | grep -v $$ | grep -v grep | egrep '\/usr\/sbin\/httpd' | wc -l`

main() {
    bounce=0
    timestampit
    datesay Looking for pidfile ${pidfile}
    ls -l ${pidfile}
    if [ -f ${pidfile} ]; then oldpid=`cat ${pidfile}`; else oldpid=0; fi
    datesay PID claims to be ${oldpid}
    [ ${oldpid} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
    portholder=`getportholder ${squidtcpport}`
    datesay PID ${portholder} owns TCP port ${squidtcpport}
    [ ${portholder:-0} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
    [ ${portholder:-0} -ne ${oldpid:-0} ] && bounce=$(( ${bounce} + 1 ))
    ncresponse=`checknc ${squidtcpport}`
    datesay GOT ${ncresponse} response\(s\) from ${squidtcpport}
    [ ${ncresponse:-0} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
    datesay ${mydaemon} has ${bounce} reasons to restart!
    [ ${bounce} -gt 0 ] && bouncedaemon
}

touch ${outfile}; chmod a+r ${outfile}
main ${@} > ${outfile} 2>&1

# Configure this part
mydaemon=stunnel

# Derived, but also configurable
outfile=/tmp/check.${mydaemon}
pidfile=/var/run/${mydaemon}.pid
logfile=/var/log/check.log

# Bookkeeping
mypid=${$}
myname=${0}
mydir=`dirname ${myname}`

# Import node-specific variables
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

main() {
    bounce=0
    timestampit
    datesay Looking for pidfile ${pidfile}
    ls -l ${pidfile}
    if [ -f ${pidfile} ]; then oldpid=`cat ${pidfile}`; else oldpid=0; fi
    datesay PID claims to be ${oldpid}
    [ ${oldpid} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
    for portpair in ${clearports}
    do
        tcpport=`echo ${portpair} | awk -F: '{print $2}'`
        portname=`echo ${portpair} | awk -F: '{print $1}'`
        portholder=0
        ncresponse=0
        portholder=`getportholder ${tcpport}`
        datesay PID ${portholder} owns TCP port ${tcpport} for ${portname}
        [ ${portholder:-0} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
        [ ${portholder:-0} -ne ${oldpid:-0} ] && bounce=$(( ${bounce} + 1 ))
        ncresponse=`checknc ${tcpport}`
        datesay GOT ${ncresponse} answer\(s\) from ${tcpport} for ${portname}
        [ ${ncresponse:-0} -eq 0 ] && bounce=$(( ${bounce} + 1 ))
    done
    datesay ${mydaemon} has ${bounce} reasons to restart!
    [ ${bounce} -gt 0 ] && bouncedaemon
}

touch ${outfile}; chmod a+r ${outfile}
main ${@} > ${outfile} 2>&1

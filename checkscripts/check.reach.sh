#!/bin/bash

# Configure this part
mydaemon=reach

# Derived, but also configurable
outfile=/tmp/check.${mydaemon}
logfile=/var/log/check.log

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

main() {
    bounce=0
    timestamp=`timestampit`
    set -- ${expectedbytes}
    for nexturl in ${reachurls}
    do
        length=${1}
        bytesback=`checkcurl ${nexturl}`
        urifragment=`echo ${nexturl} | awk -F/ '{print $4}'
        datesay ${mydaemon}:  [${timestamp}] Expected ${length} got ${bytesback} from /${urifragment}
        [ ${length} -ne ${bytesback} ] && bounce=$(( ${bounce} + 1 ))
        shift
    done
    datesay ${mydaemon}:  [${timestamp}] has ${bounce} failures!
    [ ${bounce} -gt 0 ] && logmyoutfile
}

touch ${outfile}; chmod a+r ${outfile}
main ${@} > ${outfile} 2>&1

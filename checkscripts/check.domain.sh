#!/bin/bash

# Configure this part
mydaemon=domain

# Derived, but also configurable
outfile=/tmp/check.${mydaemon}
pidfile=/var/run/${mydaemon}/${mydaemon}.pid

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
    certstate=`getcertstate ${certsrcip} ${certport}`
    domain=`getdomain "${certstate}"`

    # Get around a known jwhois bug by killing stray instances
    pkill -9 whois > /dev/null 2>&1

    domainexpiration=`getdomainexpiration ${domain} ${whoishost:-NONE}`
    domainresolution=`checkdomainresolution ${domain}`

    datesay
    echo "DOMAIN:${domain}"
    echo "CERTIFICATE:${certstate}"
    echo "${domainexpiration}"
    echo "RESOLUTION:${domainresolution:-0}"

}

touch ${outfile}; chmod a+r ${outfile}
main ${@} > ${outfile} 2>&1

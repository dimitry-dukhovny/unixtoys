Check Scripts
#############

* Created 20170607.1014Z
* Maintained in https://github.com/dimitry-dukhovny/unixtoys/

* You only need...

  * check.functions.sh
  * check.config.sh
  * check.simplified.sh

* You will probably want...

  * check.domain.sh
  * check.apache.sh

.. toctree::
..

check.functions.sh
==================

.. code-block:: bash

  datesay() # Say things in syslog format
  logit() # Use datesay() to log something
  timestampit() # Leave this alone.  Algebraic dates are cool.
  bouncedaemon() # Daemon controls # Restart daemon by description; must match init.d script name # TODO replace with systemd crap
  killdaemon() # Issue a kill to a running process by description # TODO replace with systemd crap
  getportholder() # This takes a port number as a parameter and returns a process or 0
  getcertstate() # Fetches a certificate from an ssl dialog and extracts the CN and expiry
  getdomain() # Extracts the probable domain from a URL as delivered by getcertstate().
  getdomainexpiration() # Fetches domain registration expiry from a variety of whois formats
  checkdomainresolution() # Fetches IP and compares it to expected address
  checknc() # Check if a port is taking traffic
  checkcurl() # Run a cert-agnostic curl and count the characters we get back
  checksmtp() # See if a port is a real ESMTP port
  checksmtpssl() # Same as checksmtp(), but with TLS
  checkssl() # Port check with openssl s_client
  isrunningpid() # Echo how many instances of a pid are in the process table. #  Values should be 0 or 1.  Anything else is madness.
  dumpwrap() # Start a tcpdump before a command and stop it afterward
  logmyoutfile() # Dump outfile contents to the defined logfile
..

check.config.sh
===============

* All purpose configuration file.

* Use this for any environment overrides you want.

check.simplified.sh
===================

* Summary tool for what the subordinate checks reveal.

* Formatted so good things like Nagios and evil things like Solarwinds can harvest the output.

check.apache.sh
===============

* Checks Apache HTTPD for functionality.

check.domain.sh
===============

* Checks domain validity.

* Checks cert state and provides a countdown timer with warnings.

check.postfix.sh
================

* Checks the function of Postfix.

check.reach.sh
==============

* Primitive transaction check for reachable sites.

check.squid.sh
==============

* Checks Squid proxy for functionality.

check.tomact_and_mail.sh
========================

* Checks Tomcat application server.

* Checks Postfix.

check.tunnels.sh
================

* Checks plain text ports.

* Checks the stunnel wrapper around them.

* Requires *very* fiddly configuration.

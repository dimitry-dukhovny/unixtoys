# unixtoys
Pile of scripts, filtered only by whether they have ever been in production somewhere

## ddpwprint.py
Print passwords in phonetics.  My favorite usage:
```
$ pwgen -y 16 | ./ddpwprint.py

--
Password:  tai@seedeiPahch6

         tango
         alpha
         india
         at_sign
         sierra
         echo
         echo
         delta
         echo
         india
         upper_papa
         alpha
         hotel
         charlie
         hotel
         six
```

## skineffect.py
This is messy stuff for some oil well skin effect arithmetic out of a friend's textbook.  If you are not that friend, you probably do not need this.
All constants come from Karakas, M. and S. Tariq's "Semi-analytical production models for perforated completions" in 1988.

## splunkcheck.sh
The hard-coded values are the result of my generating this script from a Jinja2 script template.  Feel free to modify those.
Anything in *main()* can change without affecting the meat of the script.

```
$ ./splunkcheck.sh
Usage:
./splunkcheck.sh <SPLUNKDIR> [<LABEL>]
  SPLUNKDIR is required, but is usually /opt/splunk
  LABEL is optional and determines the output file names in /tmp
$ ./splunkcheck.sh /opt/splunk SPLUNK
$ cat /tmp/SPLUNK.err # The explanatory output, color-coded
SPLUNK: mongod listens on 0.0.0.0:8191
SPLUNK: splunkd listens on 0.0.0.0:8089 0.0.0.0:8000
INFO: Your timerange was substituted based on your search string
SPLUNK: auto_generated_pool_download-trial 0.0 0.5 0.0 No
SPLUNK: MONGOFAIL 0
SPLUNK: APPFAIL 0
SPLUNK: DISKFAIL 0
SPLUNK: SPLUNKFAIL 0
SPLUNK: SPLUNKLICFAIL 0
SPLUNK: SWAPFAIL 0
$ cat /tmp/SPLUNK.out # The single key-value pair for monitoring
FAILURE_REASONS 0
```

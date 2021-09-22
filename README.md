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

## splunkcheck.sh
The hard-coded values are the result of my generating this script from a Jinja2 script template.  Feel free to modify those.
Anything in *main()* can change without affecting the meat of the script.

import os
import sys
import getopt
import urlparse
import urllib
import urllib2
import BaseHTTPServer
from cPickle import Pickler, Unpickler


class IDRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def run(self):
        try:
            self.counter_file = os.environ.get('counter')
            self.get_id()
        except:
            self.send_response(400)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            raise
    do_GET = run

    def getCounter(self, key):
        # initialise counter
        try:
            f = open(self.counter_file, 'r+')
            self._counters = Unpickler(f).load()
        except:
            f = open(self.counter_file, 'w+')
            self._counters = {}
        f.close()
        if not self._counters.has_key(key):
            self._counters[key] = 0
        return self._counters[key]

    def setCounter(self, key, count):
        self._counters[key] = count
        f = open(self.counter_file, 'r+')
        p = Pickler(f)
        p.dump(self._counters)
        f.close()

    def register_igsn(self, igsn):
        username = 'adam.brown@evbane.com'
        password = 'n9B@Bb00O5JyZ!Np'

        xml_content = '''
<samples>
    <sample>
        <user_code>%(user_code)</user_code>
        <sample_type>Individual Sample</sample_type>
        <material>Rock</material>
        <igsn>%(igsn)</igsn>
        <name>TestSample123</name>
        <classification>Igneous>Plutonic>Felsic</classification>
        <description>arkose</description>
        <age_min>6.5</age_min>
        <age_max>13</age_max>
        <collection_method>Grab</collection_method>
        <latitude>35.5134</latitude>
        <longitude>-117.3463</longitude>
        <elevation>781.4</elevation>
        <primary_location_name>Lava Mountains, Mojave Desert, California</primary_location_name>
        <country>United States</country>
        <province>California</province>
        <county>San Bernardino</county>
        <collector>J. E. Andrew</collector>
        <collection_start_date>January 01, 2010</collection_start_date>
        <original_archive>University of Kansas</original_archive>
    </sample>
</samples>''' % locals()

        # 1. Sample registration web service
        print 'Attempting sample registration'
        sample_registration_service_url = 'http://app.geosamples.org/webservices/uploadservice.php'

        http_body = urllib.urlencode({
            'username': username,
            'password': password,
            'content': ''
        })

        http_headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
        req = urllib2.Request(sample_registration_service_url, http_body, http_headers)
        try:
            handler = urllib2.urlopen(req)
            print handler.getcode()
            print handler.headers.getheader('content-type')
            print handler.read()

        except urllib2.HTTPError as httpError:
            print httpError.read() # This might happen, for example, if the sample ID already exists.
        print '\n'

    def get_id(self):
        batch_size = None
        command = self.command.lower() 
        if command == 'get' and self.path.find('?') != -1:
            key, qs = self.path.split('?', 1)
            data = urlparse.parse_qs(qs)
            try:
                batch_size = int(data['batch_size'][0])
            except:
                batch_size = None
        else:
            key = self.path

        prev_count = self.getCounter(key)
        next_count = prev_count + 1
        if batch_size:
            last_count = prev_count + batch_size
        else:
            last_count = next_count 
        self.setCounter(key, last_count)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        # Register IGSN here:
        next_igsn = "IEEVB" + base36encode(next_count).zfill(4)

        self.register_igsn()





        # TODO: Prefix needs to be configurable.
        self.wfile.write(next_igsn)


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
 
    base36 = ''
    sign = ''
 
    if number < 0:
        sign = '-'
        number = -number
 
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36


def base36decode(number):
    return int(number, 36)


# Copied and modified roundup-server code - thanks Richard Jones
def usage(message=''):
    if message:
        message = 'Error: %(error)s\n\n'%{'error': message}
    print '''%(message)sUsage:
id-server [-f counter] [-n hostname] [-p port] [-l file] [-d file]

  -f: counter file
  -n: sets the host name
  -p: sets the port to listen on
  -l: sets a filename to log to (instead of stdout)
  -d: run the server in the background and on UN*X write the server's PID
      to the nominated file. Note: on Windows the PID argument is needed,
      but ignored.

  Call the ID server with the key for which you want a count as path.
  E.g. calling
    http://<hostname>:<port>/Key
  repeatedly will return 1, 2, 3, etc. To start counting at a particular
  number (e.g. to skip a range of numbers), pass 'count_from' as a
  parameter:
    http://<hostname>:<port>/Key?count_from=104
  This will return 104, or (if 104 has already been issued) the next
  available number.

'''%locals()
    sys.exit(0)


def abspath(path):
    ''' Make the given path an absolute path.

        Code from Zope-Coders posting of 2002-10-06 by GvR.
    '''
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    return os.path.normpath(path)


def daemonize(pidfile):
    ''' Turn this process into a daemon.
        - make sure the sys.std(in|out|err) are completely cut off
        - make our parent PID 1

        Write our new PID to the pidfile.

        From A.M. Kuuchling (possibly originally Greg Ward) with
        modification from Oren Tirosh, and finally a small mod from me.
    '''
    # Fork once
    if os.fork() != 0:
        os._exit(0)

    # Create new session
    os.setsid()

    # Second fork to force PPID=1
    pid = os.fork()
    if pid:
        pidfile = open(pidfile, 'w')
        pidfile.write(str(pid))
        pidfile.close()
        os._exit(0)         

    os.chdir("/")         
    os.umask(0)

    # close off sys.std(in|out|err), redirect to devnull so the file
    # descriptors can't be used again
    devnull = os.open('/dev/null', 0)
    os.dup2(devnull, 0)
    os.dup2(devnull, 1)
    os.dup2(devnull, 2)


def run():
    ''' Script entry point - handle args and figure out what to to.
    '''
    # time out after a minute if we can
    import socket
    if hasattr(socket, 'setdefaulttimeout'):
        socket.setdefaulttimeout(120)

    hostname = ''
    port = 8081
    pidfile = None
    logfile = None
    user = None
    counter = None
    try:
        # handle the command-line args
        try:
            optlist, args = getopt.getopt(sys.argv[1:], 'f:n:p:u:d:l:h')
        except getopt.GetoptError, e:
            usage(str(e))

        for (opt, arg) in optlist:
            if opt == '-f': counter = arg
            elif opt == '-n': hostname = arg
            elif opt == '-p': port = int(arg)
            elif opt == '-u': user = arg
            elif opt == '-d': pidfile = abspath(arg)
            elif opt == '-l': logfile = abspath(arg)
            elif opt == '-h': usage()

        if hasattr(os, 'getuid'):
            # if root, setuid to the running user
            if not os.getuid() and user is not None:
                try:
                    import pwd
                except ImportError:
                    raise ValueError, "Can't change users - no pwd module"
                try:
                    uid = pwd.getpwnam(user)[2]
                except KeyError:
                    raise ValueError, "User %(user)s doesn't exist"%locals()
                os.setuid(uid)
            elif os.getuid() and user is not None:
                print 'WARNING: ignoring "-u" argument, not root'

            # People can remove this check if they're really determined
            if not os.getuid() and user is None:
                raise ValueError, "Can't run as root!"

        if counter is None:
            raise ValueError, "You have to specify the location of the counter file."
        else:
            os.environ['counter'] = counter

    except SystemExit:
        raise
    except:
        exc_type, exc_value = sys.exc_info()[:2]
        usage('%s: %s'%(exc_type, exc_value))

    # we don't want the cgi module interpreting the command-line args ;)
    sys.argv = sys.argv[:1]
    address = (hostname, port)

    # fork?
    if pidfile:
        if not hasattr(os, 'fork'):
            print "Sorry, you can't run the server as a daemon on this" \
                'Operating System'
            sys.exit(0)
        else:
            daemonize(pidfile)

    # redirect stdout/stderr to our logfile
    if logfile:
        # appending, unbuffered
        sys.stdout = sys.stderr = open(logfile, 'a', 0)

    httpd = BaseHTTPServer.HTTPServer(address, IDRequestHandler)
    print 'ID server started on %(address)s'%locals()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Keyboard Interrupt: exiting'

if __name__ == '__main__':
    run()

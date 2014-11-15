from gevent import monkey; monkey.patch_all()

from bottle import route, run,request,get,post

from functools import wraps
import json
import commands
import signal
import time


class Failing(Exception):
    pass


def timeout(signum, frame):
    print 'task is timeout'


def retry(retries,limittime):
    def repl(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            i = 0
            signal.signal(signal.SIGALRM, timeout)
            signal.alarm(limittime)


            while i < retries:
                print 'Retry count:',i
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    i += 1
                    if retries == i:
                        raise Failing(e)
        return wrapper
    return repl

@get('/get',method='GET')
@retry(1,3)
def keyget():
    user = request.query.get('user')
    port = request.query.get('port')
    host = request.query.get('host')
    info = commands.get(user,host,port,'raw')
    
    return info

@route('/add',method='POST')
def keyadd():
    data = json.loads(request.body.read())
    user = data['user']
    host = data['host']
    port = data['port']
    keylist = data['keylist']
    info = commands.add(user,host,port,keylist)
    return info

@route('/delete',method='DELETE')
def keydelete():
    data = json.loads(request.body.read())
    user = data['user']
    host = data['host']
    port = data['port']
    keyid = data['keyid']
    return 'ok'
run(host='0.0.0.0', port=8080, server='gevent')

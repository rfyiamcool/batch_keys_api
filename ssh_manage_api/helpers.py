import sys
import os
import logging
from getpass import getpass
from tempfile import NamedTemporaryFile

from sh import ssh, scp, ErrorReturnCode_1


class NoSuchFileError(Exception):
    pass


def parse_ssh_string(ssh_string):
    """
        >>> parse_ssh_string('user@host:13')
        ('user', 'host', 13)
        >>> parse_ssh_string('user@host')
        ('user', 'host', 22)
        >>> parse_ssh_string('host:13')[1:]
        ('host', 13)
        >>> parse_ssh_string('host')[1:]
        ('host', 22)
        >>> import os
        >>> os_user = os.environ.get('USER')
        >>> parse_ssh_string('host:13')[0] == os_user
        True
        >>> parse_ssh_string('host')[0] == os_user
        True
    """

    user = os.environ.get('USER')
    port = 22

    if '@' in ssh_string:
        user, ssh_string = ssh_string.split('@')

    if ':' in ssh_string:
        host, port = ssh_string.split(':')
        port = int(port)
    else:
        host = ssh_string

    return user, host, port


def load_local_keys(key_files):
    if not key_files:
        key_files.append(os.path.expanduser('~/.ssh/id_rsa.pub'))
        logging.info('Loading local id_rsa.pub')
    else:
        logging.info('Loading keys: {0}'.format(', '.join(key_files)))

    local_keys = {}

    for key_file in key_files:
        with open(os.path.expanduser(key_file), 'rt') as f:
            key_data = f.read().strip()
            local_keys[key_file] = key_data

    return local_keys


class Controller(object):
    out = b''
    user = None
    host = None
    port = 22
    password = None

    def __init__(self, user, host, port=22):
        self.user = user
        self.host = host
        self.port = port or 22

    def __call__(self, *args, **kwargs):
        logging.debug('run command: "{0}"'.format(self.process.ran))

    def out_iteract(self, char, stdin, process):
        if isinstance(char, str):
            self.out += char.encode('utf8')
        else:
            self.out += char

        out = self.out.decode('utf-8', errors='ignore')

        if out.endswith('password: '):
            self.clear()
            stdin.put(self.get_password() + '\n')

    def get_password(self):
        logging.debug('request password')

        if not self.password:
            prompt = '{c.user}@{c.host}:{c.port} - need password: '.format(c=self)
            self.password = getpass(prompt)

        return self.password

    def clear(self):
        self.out = b''
        self.error = b''

    def wait(self):
        return self.process.wait()


class SSHController(Controller):
    no_such_file_error = False

    def __call__(self, *args, **kwargs):
        self.process = ssh(
                            '-o UserKnownHostsFile=/dev/null',
                            '-o StrictHostKeyChecking=no',
                            '-o LogLevel=quiet',
                            '{0}@{1}'.format(self.user, self.host),
                            '-p', self.port,
                            'LANG=C', *args,
                            _out=self.out_iteract, _out_bufsize=0, _tty_in=True,
                            **kwargs)

        super(SSHController, self).__call__(*args, **kwargs)

    def out_iteract(self, char, stdin, process):
        super(SSHController, self).out_iteract(char, stdin, process)

        out = self.out.decode('utf-8', errors='ignore')

        if out.endswith('No such file or directory'):
            self.no_such_file_error = True
            process.kill()


class SCPController(Controller):
    def __call__(self, local_file, remote_file, **kwargs):
        self.process = scp(
                            '-o UserKnownHostsFile=/dev/null',
                            '-o StrictHostKeyChecking=no',
                            '-o LogLevel=quiet',
                            '-P', self.port,
                            local_file,
                            '{0}@{1}:{2}'.format(self.user, self.host, remote_file),
                            _out=self.out_iteract, _out_bufsize=0, _tty_in=True,
                            **kwargs)

        super(SCPController, self).__call__(local_file, remote_file, **kwargs)


def get_authorized_keys(controller):
    logging.info('{c.user}@{c.host}:{c.port} - getting authorized_keys'.format(c=controller))

    try:
        controller.clear()
        controller('cat ~/.ssh/authorized_keys')
        controller.wait()

    except ErrorReturnCode_1:
        if controller.no_such_file_error:
            raise NoSuchFileError()
        else:
            logging.critical(controller.out.decode('utf8', errors='ignore'))
            raise

    except Exception:
        logging.critical(controller.out.decode('utf8', errors='ignore'))
        raise

    out = controller.out.decode('utf8', errors='ignore')
    return [line.strip() for line in out.split('\n')]


def create_authorized_keys_file(controller):
    logging.info('{c.user}@{c.host}:{c.port} - creating ~/.ssh'.format(c=controller))

    try:
        controller.clear()
        controller('mkdir -p ~/.ssh')
        controller.wait()

    except ErrorReturnCode_1:
        if controller.no_such_file_error:
            raise NoSuchFileError()
        else:
            logging.critical(controller.out.decode('utf8', errors='ignore'))
            raise

    except Exception:
        logging.critical(controller.out.decode('utf8', errors='ignore'))
        raise


def set_authorized_keys(controller, keys):
    logging.info('{c.user}@{c.host}:{c.port} - writing authorized_keys'.format(c=controller))

    if sys.version_info.major >= 3:
        buffering = 'buffering'
    else:
        buffering = 'bufsize'

    with NamedTemporaryFile('w+b', **{buffering: 0}) as tmp:
        data = '\n'.join(keys)
        tmp.write(data.encode('utf8'))

        if data and data[-1] != '\n':
            tmp.write(b'\n')

        try:
            controller.clear()
            controller(tmp.name, '~/.ssh/authorized_keys')
            controller.wait()
        except Exception:
            logging.critical(controller.out.decode('utf8', errors='ignore'))
            raise

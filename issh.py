# -*- coding: utf-8 -*-

import os
import sys
import stat
import logging
import paramiko

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

console = logging.StreamHandler()
console.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))

SSH_PORT = 22


def get_logger(name):
    l = logging.getLogger(name)
    l.addHandler(console)
    return l


def get_ssh(hostname,
            port=SSH_PORT,
            username=None,
            password=None):
    """
    Create a new SSHClient.
    :param hostname: 
    :param port: 
    :param username: 
    :param password: 
    :return: ssh client 
    """

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password, look_for_keys=False)
    ssh.open_sftp()
    return ssh


def get_sftp(hostname,
             port=SSH_PORT,
             username=None,
             password=None,
             ssh_client=None):
    """
    Create an SFTP client channel from an ssh_client or some server login meta info.
    :param hostname:
    :param port:
    :param username:
    :param password:
    :param ssh_client:
    :return: a new `.SFTPClient` object, referring to an ssh session (channel) across the transport
    """
    if ssh_client is not None:
        return ssh_client.open_sftp()

    t = paramiko.Transport(hostname, port)
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)

    return sftp


def is_blank(s):
    """Check string is none or empty
    :rtype: bool
    """
    return not (s and s.strip())


def rexists(sftp, path):
    """os.path.exists for paramiko's SCP object
    """
    try:
        statout = sftp.stat(path)
    except IOError, e:
        if e[0] == 2:
            return False
        raise
    else:
        return True


def risdir(sftp, path):
    """Check remote path is a directory
    """
    try:
        lstatout = sftp.lstat(path).st_mode
        return stat.S_ISDIR(lstatout)
    except IOError, e:
        return False


class SSH(object):
    def __init__(self, hostname, port=SSH_PORT, username=None, password=None):
        """
        SSH Client wrapper,support both ssh command and push multiple file(s) or directory
        :param hostname: 
        :param port: 
        :param username: 
        :param password: 
        """
        self.logger = get_logger('ssh')
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.sftp = None
        self.ssh = get_ssh(self.hostname, self.port, self.username, self.password)

    def __del__(self):
        self.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _log(self, level, msg, *args):
        if isinstance(msg, list):
            for m in msg:
                self._log(level, m, *args)
        else:
            msg = msg.replace('%', '%%')
            self.logger.log(level, "[ssh %s]" + msg, *([self.host] + list(args)))

    def get_sftp(self):
        sftp = self.sftp
        if sftp is None:
            sftp = self.sftp = get_sftp(self.hostname, self.port, self.username, self.password, self.ssh)
        return sftp

    def mkdir(self, path, mode=511, ignore_existing=False, intermediate=False):
        """
        Enhance mkdir cmd 
        """
        self._log(DEBUG, '> mkdir %s' % path)

        sftp = self.get_sftp()

        if not is_blank(path) and not rexists(sftp, path):
            path = path.rstrip(os.sep)
            try:
                sftp.mkdir(path, mode)
            except IOError as e:
                if intermediate:
                    dir = path.rsplit(os.sep, 1)[0]
                    if not dir:
                        raise
                    self.mkdir(dir, mode, True, True)
                    return sftp.mkdir(path, mode)
                if ignore_existing:
                    pass
                else:
                    raise

    def _put_dir(self, source, target):
        assert target.startswith("/"), "%s must be absolute path" % target

        self._log(DEBUG, '> put %s => %s' % (source, target))

        for p in os.listdir(source):
            rp = os.path.join(target, p)
            lp = os.path.join(source, p)
            if os.path.isfile(lp):
                self.get_sftp().put(lp, rp)
            else:
                self.mkdir(rp, ignore_existing=True, intermediate=True)
                self._put_dir(lp, rp)

    def put(self, src, dest):
        """
        Copy a local file to the remote server by SFTP
        """

        assert os.path.exists(src), 'fatal: PUT failed, No such file or directory: {0}'.format(src)

        if os.path.isdir(src):
            # Each of the following commands copies the files in the same way,
            # including their setting of the attributes of /dest/foo:
            #
            #   issh -s /src/foo -d /dest
            #   issh -s /src/foo/ -d /dest/foo
            #
            if not src.endswith(os.sep):
                dest = os.path.join(dest, os.path.basename(src))

            self._put_dir(src, dest)

        else:
            sftp = self.get_sftp()
            filename = os.path.basename(src)
            dirname = os.path.dirname(dest)

            # check whether the dest is directory
            if dest.endswith(os.sep):
                dirname = dest
                dest = os.path.join(dest, filename)

            # prepare for desc dir
            self.mkdir(dirname, ignore_existing=True, intermediate=True)

            self._log(DEBUG, '> put %s => %s' % (src, dest))

            try:
                sftp.put(src, dest)
            except IOError as e:
                if risdir(sftp, dest):
                    sftp.put(src, os.path.join(dest, filename))

    def exec_command(self, command, environment=None):
        """
        Execute command, output the stdout and stderr results.
        :param command: 
        :param environment: 
        :return: 
            True if all of the command sequence run success
        """

        if not isinstance(command, (list, tuple)):
            command = [command]

        try:
            self._log(DEBUG, '>exec %s' % command)
            for c in command:
                if is_blank(c):
                    continue

                stdin, stdout, stderr = self.ssh.exec_command(c)

                # console stdout & error
                for line in stdout.read().splitlines():
                    print(line)
                for line in stderr.read().splitlines():
                    print(line)

                # success is 0
                exit_code = stdout.channel.recv_exit_status()

                if exit_code != 0:
                    print('exit code: %s' % exit_code)
                    sys.exit(exit_code)

            return True

        except paramiko.AuthenticationException as e:
            print('fatal: %s' % e)
            try:
                self.close()
            except:
                pass

            sys.exit(1)
        except Exception as e:
            self._log(ERROR, '*** Caught exception: %s: %s, command: %s' % (e.__class__, e, command))
            try:
                self.close()
            except:
                pass

            sys.exit(1)

    def close(self):
        if hasattr(self, 'ssh') and self.ssh is not None:
            self.ssh.close()
            if self.sftp is not None:
                self.sftp.close()
            self.ssh = None


if __name__ == '__main__':
    import argparse

    logger = get_logger('ssh')

    parser = argparse.ArgumentParser(
        description='SSH client supports with password explicitly.\n'
                    ' (by allex_wang <http://iallex.com/> MIT Licensed)\n'
                    ' (by sloong:sloong@protonmail.com , MIT Licensed)')

    parser.add_argument('hostname', metavar='<hostname>', help='[user@]hostname')

    parser.add_argument('command', metavar='<command>', help='[command] The command to execute in remote.')

    parser.add_argument('-u', '--username', nargs='?', help='username')
    parser.add_argument('-p', '--password', nargs='?', help='password')
    parser.add_argument('-P', '--port', default=22, type=int, nargs='?', help='port')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Verbose mode.')

    parser.add_argument('-s', '--src', nargs='?', help='Optional a local source file to transfer.')
    parser.add_argument('-d', '--dest', nargs='?', help='The destination file path to the remote.')

    args = parser.parse_args()
    _hostname = args.hostname

    # init logger level
    logger.setLevel((INFO, DEBUG)[args.verbose])

    if _hostname is not None and '@' in _hostname:
        parts = _hostname.split('@')
        args.username = parts[0]
        args.hostname = parts[1]

    logger.debug('ARGS => %s' % vars(args))
    logger.debug('Initialize ssh connect => %s@%s:%s...' % (args.username, args.hostname, args.port))

    try:
        client = SSH(args.hostname, username=args.username, password=args.password, port=args.port)

        logger.debug('Connect success.')

        if not is_blank(args.src):
            if is_blank(args.dest):
                print('failed: No such destination path')
                sys.exit(1)

            logger.info('> Push to remote:%s => %s:%s' % (args.src, args.dest))

            client.put(args.src, args.dest)

        if not is_blank(args.command):
            client.exec_command(args.command)

        client.close()

    except Exception as e:
        if args.verbose:
            logger.debug('Exception has occurred', exc_info=1)
        else:
            logger.error("*** Caught exception: %s: %s" % (e.__class__, e))

        sys.exit(1)

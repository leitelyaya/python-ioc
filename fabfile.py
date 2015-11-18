from fabric.decorators import task

from fabric.contrib.console import confirm
from fabric.operations import local
from fabric.tasks import execute
import os

here = os.path.abspath(os.path.dirname(__file__))

about = {}
# read about values
with open(os.path.join(here, 'pythonioc', '__about__.py'), 'r') as f:
    exec(f.read(), about)

def incrementVersion(what):
    if what not in ['major', 'minor', 'micro']:
        raise Exception("Need at least one version number to increment")

    (major, minor, micro) = about['__version__'].split('.')
    if what == 'major':
        major = int(major) + 1
        minor = 0
        micro = 0
    elif what == 'minor':
        minor = int(minor) + 1
        micro = 0
    else:
        micro = int(micro) + 1

    newVersion = '%s.%s.%s' % (major, minor, micro)



    return newVersion

@task
def release(message, what='micro'):
    execute(check)
    newVersion = incrementVersion(what)

    if confirm("Current version is %s. New version would be %s. Uploading now?" % (about['__version__'], newVersion), default=True):
        local("sed -i 's/^__version__.*$/__version__ = \"%s\"/g' %s" % (newVersion, 'pythonioc/__about__.py'))

        local('python setup.py sdist')
        local('twine upload dist/pythonioc-%s.tar.gz' % newVersion)

    if confirm('Commit it?', default=True):
        local('git commit -m "%s" .' % message)
        local('git tag -a v%s -m "%s"' % (newVersion, message))


@task
def check():
    local('trial pythonioc')

@task
def upgrade():
    local('sudo pip install pythonioc --upgrade')

@task
def localInstall():
    execute(check)
    local('sudo python setup.py install')

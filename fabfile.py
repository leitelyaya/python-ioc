from fabric.decorators import task

import pythonioc
from fabric.contrib.console import confirm
from fabric.operations import local
from fabric.tasks import execute

def incrementVersion(what):
    if what not in ['major', 'minor', 'micro']:
        raise Exception("Need at least one version number to increment")
    
    (major, minor, micro) = pythonioc.__version__.split('.')
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
        
    if not confirm("Current version is %s. New version would be %s. Ok?" % (pythonioc.__version__, newVersion), default=True):
        return
    
    local("sed -i 's/^__version__.*$/__version__ = \"%s\"/g' %s" % (newVersion, 'pythonioc/__init__.py'))
    
    local('python setup.py sdist')
    local('twine upload dist/pythonioc-%s.tar.gz' % newVersion)
    

@task
def release(what='micro'):
    execute(check)
    incrementVersion(what)


@task
def check():
    local('trial pythonioc')
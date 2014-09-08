from distutils.core import setup
import pythonioc
setup(name='pythonioc',
      packages=['pythonioc'],
      description='simplistic dependency injection container for python',
      author='Franz Eichhorn',
      author_email='frairon@googlemail.com',
      url='https://bitbucket.org/eh14/python-ioc',
      license='MIT',
      version=pythonioc.__version__,
      )

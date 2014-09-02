from distutils.core import setup
setup(name='pythonioc',
      packages=['pythonioc'],
      description='simplistic dependency injection container for python',
      author = 'Franz Eichhorn',
      author_email = 'frairon@gmail.com'
      version='0.1',
      py_modules=['serviceproxy.py',
                  'serviceregistry.py'],
      )
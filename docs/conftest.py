import doctest
from doctest_setup import setup_doctest
import  os
import sys

# Set Fake MUSICLANG_API_KEY
os.environ['MUSICLANG_API_KEY'] = 'FAKE_API'
setup_doctest(doctest)
# -----------------------------------------------------------------------------
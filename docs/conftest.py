import doctest
from doctest_setup import setup_doctest
import  os
import sys

# Set Fake API_KEY
os.environ['API_KEY'] = 'FAKE_API'
setup_doctest(doctest)
# -----------------------------------------------------------------------------
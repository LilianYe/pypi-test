# pypi-test
test code for submit a package to testpypi.

I mostly refer to the the blog http://peterdowns.com/posts/first-time-with-pypi.html, however some content is out of date. 

## Create your accounts
Create an account on https://testpypi.python.org/pypi. 

## No need to create .pypirc configuration file

## Prepare you package
This step is same to the step 3 in that blog. 
Note __init__.py is necessary. 

## Upload you package to PyPI Test
```
python setup.py sdist
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
You will be asked to type in you username and password. 
If everything works fine, you are succeed. 

## install your package
```
sudo pip install --index-url https://test.pypi.org/simple/ trdbhelp
```
try in python if succeed
```
import trdbhelp
```

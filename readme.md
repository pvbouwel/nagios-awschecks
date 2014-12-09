BETA-Warning
============
This project is pushed to github but as you might expect by reviewing the version number it is in an early stage.  This
means it is still subject to change and likely to contain some bugs.

Description
===========
This project is just a nagios check that allows to verify whether your AWS resources are properly tagged.  If you have a
tagging policy you can use this check from Nagios to verify whether mandatory tags are indeed set.

Usage
=====
 
AWS authentication
------------------
As boto is used it is possible to use a .boto credential file.  But as shown in the print_usage above it is also 
possible to pass a aws_access_key_id and a aws_secret_access_key to authenticate. A policy will be added to this 
documentation that shows the rights that are needed since leaving credentials on a system can pose a security risk, thus
 it is wise too limit the impact one can do with leaked credentials.

###Policy example

Dependencies
============
Regular print_usage
-------------

###boto
pip install boto

Development
-----------

### moto
This Python module is used to mock the AWS services
...
pip install moto
...
### nose
This Python module is used to find and run the tests in order to report on the tests.
pip install nose

Tests
=====
In order to run the tests make sure you have all the 'Development' and 'Regular print_usage' dependencies installed.  
Either on your system or in a virtual_env (if the latter be sure to activate it).  Next go to the root of the source 
directory and launch `nosetests`

Contribute
==========
I am open to contributions.  You can fork, alter and create a Pull request.  There are multiple ways to contribute:
* add functionality
* extends tests
* improve documentation
* submit issues
* add things I forgot to put in this list

I do however plan to be as backwards compatible as possible, so unless there is a very good reason to break compatiblity
keep this in mind.

Thanks already for the effort!
Description
===========
This project is just a nagios check that allows to verify whether your AWS resources are properly tagged.  If you have a
tagging policy you can use this check from Nagios to verify whether mandatory tags are indeed set.

Usage
=====
 
AWS authentication
------------------
As boto is used it is possible to use a .boto credential file.  But as shown in the print_usage above it is also possible to 
pass a aws_access_key_id and a aws_secret_access_key to authenticate. A policy will be added to this documentation that
shows the rights that are needed since leaving credentials on a system can pose a security risk, thus it is wise too 
limit the impact one can do with leaked credentials.

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
In order to run the tests make sure you have all the 'Development' and 'Regular print_usage' dependencies installed.  Either 
 on your system or in a virtual_env (if the latter be sure to activate it).  Next go to the root of the source directory
  and launch `nosetests`

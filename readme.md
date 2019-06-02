# Warning

This project is not actively maintained. The last update was just to avoid security issues.
Since this project was based on boto2 it likely won't see active development in the future.
Also note that it is Python 2 only so given that Python 2 is on its deprecation path this project is not recommended for
new projects.

# Description

This project is meant to become an utility to aid implementation of Nagios checks for AWS in python.  The goal is to 
 provide the possibility to only provide the check logic of what you want to check.  This project would handle the 
 generic stuff that needs to be done for AWS checking.  Currently it is seen that the following functionality should be
 provided by this project:
 
  * Provide a CLI api for launching the check
  * Provide AWS authentication possibilities
  * Provide region(s) support
  * Provide 1 example check implementation
  * Provide the possibility for users to write checks that make use of this project (TBD)
  
## Regions support 

A nagios-awscheck takes a region as parameter.  If 'ALL' is passed as value the check will verify all regions that are 
publicly available.  Beware however that at the moment of writing the following regions were accessible upon request (
and thus not considered publicly available):
* cn-north-1
* us-gov-west-1

You can check in these regions when explicitly specifying them.

# Usage

## Installation
### Local environment
Clone the git repository.  Make sure the PYTHONPATH System variable also contains the root of this cloned git repo.
 E.g.
 ```
 cd /tmp/
 git clone git@github.com:pvbouwel/nagios-awschecks
Cloning into 'nagios-awschecks'...
remote: Counting objects: 125, done.
remote: Compressing objects: 100% (116/116), done.
remote: Total 125 (delta 70), reused 0 (delta 0)
Receiving objects: 100% (125/125), 23.50 KiB | 0 bytes/s, done.
Resolving deltas: 100% (70/70), done.
Checking connectivity... done
 export PYTHONPATH="$PYTHONPATH:/tmp/nagios-awschecks"
 ```
 
Install the requirements for the app `pip install /tmp/nagios-awschecks/requirements.txt` 
 
Then it can be executed using `python /tmp/nagios-awschecks/awschecks/nagioscheckscli.py --region ALL --check awstagscheck --warning Owner --critical Bill --resource instance,volume`


### System wide
#### From Source
To be done (setup.py must be revised and tested)

#### Pip
Nice to have for the future
 
## AWS authentication

As boto is used it is possible to use a .boto credential file.  But as shown in the print_usage above it is also 
possible to pass a aws_access_key_id and a aws_secret_access_key to authenticate. A policy will be added to this 
documentation that shows the rights that are needed since leaving credentials on a system can pose a security risk, thus
 it is wise too limit the impact one can do with leaked credentials.

###Policy example

# Dependencies

## Regular usage

## Development

### Dependencies
These are all mentioned in requirements-dev.txt , these dependencies are necessary to run all the tests.

Currently there is no release of moto in pip that can be used.  In requirements-dev.txt the commit of the moto repo is
mentioned which can be used.  The moto repository can be found at https://github.com/spulec/moto 

# Tests

In order to run the tests make sure you have all the 'Development' and 'Regular usage' dependencies installed.  
Either on your system or in a virtual_env (if the latter be sure to activate it).  Next go to the root of the source 
directory and launch `nosetests`


# Contribute

I am open to contributions.  You can fork, alter and create a Pull request.  There are multiple ways to contribute:
* add functionality
* extends tests
* improve documentation
* submit issues
* Create additional checks for AWS using this project
* add things I forgot to put in this list

I do want to be as backwards compatible as possible.  Please keep this in mind.

Thanks already for the effort!

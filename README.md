# Target Case Study
### Candidate: Dave White, dave 4 mpls [at] gmail [dot] com, 612-695-3289
### Position: Guest Reliability Engineer

Because I had the week long deadline, I decided to do both case studies, even though it says to only do one.  In an actual workplace environment, of course I would only do what was asked, but here, I have the opportunity to show you several skills I have that might be relevant to your position.

If you prefer to just ignore one of them, then just look at the NextBus one.

## NextBus
written in Python for the command line, and adapted to the web using the Brython JavaScript library.

### Design Summary
 * I would use a scripting language typically for a task like this.  I chose Python, which I have learned recently, to show how I can learn a new language and adapt to its stylistic requirements, in this case including unit testing modules, docstrings, etc.
 * I designed it based on the theory that it could be used interactively on the command line, with command line parameters, as a Python module in another program, or as an input to another program that is reading its Standard Output.  Flexibility is good!
 * The program also runs as a module within a web page using Brython, as shown below.
 * Details about the design are in the comments at the beginning of the `nextbus.py` program.

### Running / Installing
To Use on the Web:
 * Use Chrome or Firefox or Edge (the Brython conversion library doesn't work in Internet Explorer).
 * Go [here](https://www.davewhitesoftware.com/target/nextbus.htm).
 * Just enter the information into the boxes and press the button.  
 * The identical Python code is running in your browser, providing the responses.
 
To Run Unit Tests and Command Line In Your Browser Using Repl.It:
  * Use Chrome or Firefox.
  * To run the command-line program without installing it, go [here](https://repl.it/@dave4mpls/NextBus).  Then click Run.
  * You will be prompted to enter the parameters, on the right side.
  * To run the unit tests without installing them, go [here](https://repl.it/@dave4mpls/NextBusUnitTests).  Then click Run.
  * The tests include scraping the Metro Transit user-facing website to make sure my program matches what a user would get themselves, and so depending on the timing of calling this site versus running my program, if the data changes in between, a test might fail.  However, the test program accounts for this and therefore it almost always prints "ok" meaning "all tests passed."

To Install Locally:
 * Download the `nextbus.py` program which is in `/NextBus/src/nextbus.py` in this repository.
 * Make sure you are using Python 3.
 * Make sure the requests module is installed.  If not, install it using `pip install requests` at the command line.
 * Run the program by typing `python nextbus.py`.  With no parameters, it will prompt for the route, stop, and direction.  Or, you can put the parameters on the command line, e.g. `python nextbus.py #21 Chicago west`
 
 To Run Unit Tests Locally:
  * Do all the steps above under To Install Locally.
  * Download the `nextbus_unittests.py` file from `/NextBus/tests/nextbus_unittests.py` in this repository, and put it in the same folder with the `nextbus.py` program.
  * Run the program by typing `python nextbus_unittests.py`.  
  * The tests include scraping the Metro Transit user-facing website to make sure my program matches what a user would get themselves, and so depending on the timing of calling this site versus running my program, if the data changes in between, a test might fail.  However, the test program accounts for this and therefore it almost always prints "ok" meaning "all tests passed."

 

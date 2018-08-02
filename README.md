# Target Case Study
### Candidate: Dave White, dave 4 mpls [at] gmail [dot] com, 612-695-3289
### Position: Guest Reliability Engineer

Because I had the week long deadline, I decided to do both case studies, even though it says to only do one.  In an actual workplace environment, of course I would only do what was asked, but here, I have the opportunity to show you several skills I have that might be relevant to your position.

If you prefer to just ignore one of them, then just look at the NextBus one.

[Additional code samples and live demos are available](#AdditionalCode) (including new stuff in React.JS that's not on my portfolio yet)!

## NextBus
Written in Python for the command line, and adapted to the web using the Brython JavaScript library.

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
 * The Python code is running in your browser, providing the responses.
 
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

## GetDiskUsage
Shown in PHP and also in cross-platform C, to demonstrate my abilities to create both a quick and dirty script for managing disk usage, and also a low-level cross-platform program.  (I also do C++ and Java.  I have used C and PHP extensively in the past.)

Design Notes
 * In practice I would use a scripting language like PHP for this task, it's much faster.  I only did the C version so you could see that I can go low-level if I need to, and also make it cross-platform at that level.
 * The JSON object in the design example didn't have fields, so I added a boolean indicating if an item is a directory (True) or a file (False), a field for the whole pathname, and a field for the file size.
 * Directories are listed after the files they contain, and include the total size of the whole directory in bytes.  I find this is useful when managing disk space.
 * The very last line is the original pathname you provided, and includes the size of all the files.
 * Both the C and the PHP version are UTF-8 friendly and tested on file and folder names with Unicode characters, in both Windows and Linux.

Installing and Using PHP Version
 * Download the `getdiskusage.php` program from `/GetDiskUsage/src/php_version/getdiskusage.php` on this repository.
 * Run it at the command line, providing the mount point or folder name in the command line, e.g. `php getdiskusage.php /tmp`
 * It will output the JSON listing to standard output.

Installing the C Version under Windows
 * Place `getdiskusage.c` and `tinydir.h` in a single folder; get these files from `/GetDiskUsage/src/c_version` on this repository.
 * Compile using Visual Studio.  Or, if you don't want to compile, just run the executable, available at `/GetDiskUsage/win32/getdiskusage.exe` on this repository.
 * Run the executable at a command prompt, providing a path, for example: `getdiskusage C:\temp`

Compiling and Installing the C version under Linux
 * Place `getdiskusage.c` and `tinydir.h` in a single folder; get these files from `/GetDiskUsage/src/c_version` on this repository.
 * Compile using the following `gcc` command line: `gcc -o getdiskusage getdiskusage.c`
 * Run the executable at a command prompt, providing a path, for example: `./getdiskusage /tmp`

Testing
 * Unicode was tested manually by creating files and folders with Unicode names in both Windows and Linux.
 * The results from those tests in Windows can be viewed in this repository at `/GetDiskUsage/output`.  
 * A PHP test program was created to compare the output of the C and PHP programs.  There are slightly different versions for Linux and Windows.  These are in `/GetDiskUsage/test`.  To use them, put the version for your operating system in the same folder with the PHP version and the compiled C program, and then run `php diskusagetest.php path` in Linux or `php diskusagetest_windows.php path` in Windows.  Substitute a local path on your drive for the word path.
 
## <a name="AdditionalCode"></a>Additional Code Samples

* Additional code samples are available at my [portfolio](https://www.davewhitesoftware.com).
* Also, I am working on a React web app with GitHub source [here](https://www.github.com/dave4mpls/autoaccompany) and latest working copy [here](http://www.davewhitesoftware.com/autoaccompany).  It's not done yet (playing music and MIDI connections work, recording is not implemented), but it shows how I can use a new-to-me technology (React) to develop a sophisticated web UI that works across devices.  Imagine instead of a piano keyboard, there are network notifications or other reporting or configuration settings necessary for the Guest Reliability team, and they can access them on any phone, tablet or device.  
* My ability to learn is also demonstrated by my [CodeSignal profile](https://app.codesignal.com/profile/dave_w11), where my score is in the top 5%.  CodeSignal is not just for students, it is used to recruit for professionals in the Bay Area.  My use of the site mostly involved moderate-to-difficult algorithmic problems in 10 different languages that I am learning or refreshing my memory in, including Python, C, C++, Java, JavaScript, TypeScript, etc.


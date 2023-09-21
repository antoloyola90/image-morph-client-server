# Environment

- I tested the scripts on 'macOS Catalina v10.15.7'. There might be a warning thrown if xcode is already installed but that shouldn't bother the overall.

# Solution - Issues + TODOs for production

- The logging + error handling defintely needs more time as I am sure that there are many ways to reach unhandled scenarios.
- In the client, I did try with some inaccurate images and it seemed to produce something with the required dimensions but I did not write a way to confirm if the pixels shifted as required. This is a unit test that would also be required to test the Rotate Image implementation.
- Writing the unit test for the Mean Filter seems like a redo of the unit test by opencv. Also it seems like a redo of the actual 'blur' function.
-  Overall, there are no tests for either the server or the client and I would have liked to add some.
- The setup, server, build, client runnables are bare-bone and do not cover any unknown scenarios. Would have liked to spend a bit longer on that.
- Some of my variable names were less than descriptive :P
- I have not tested on really huge files and may reach limits
- With multiple clients, the server will be a bottleneck. I have run it with 10 workers but we should increase this as our load increases. But this brings in questions of the true multiprocessing nature of python, the underlying hardware, network limitations, firewall, load-balancing algorithms; best to keep that door closed for now so that I look good :D

# FaithTech Hackathon 2021

## Overview

An experiment on matching a context describing a question with contexts describing Scripture. We assume that there is a way to take a question and extract data from it into a structure containing various pieces of information (call it `QuestionCtx`), and that there is also a way to take Scriptures and extract data from them into a different structure (call it `ScriptureCtx`). With these assumptions, we create sample versions of these structures and try to match for a given question, the Scripture which matches most closely as an answer.

## Install

1. Make sure python version 3.x is installed. This can be checked by running `python --version`. If it reveals version 2.x, then install python 3 from the applicable platform package here: https://www.python.org/downloads/release/python-3105/.
- On Mac, you can also use Homebrew: `brew install python3`

2. Install Git according to the instructions here: https://github.com/git-guides/install-git.

3. Log into https://www.github.com with your account and follow the instructions here to create a personal access token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token. After this, you do not need to be logged into your account, but it's fine to be as well. Just make sure to save your token somewhere secure that you can access again. A credential manager is a good choice.

4. Running the git commands is usually done through the Terminal on Mac or Command Prompt on Windows, or using a Git client (like https://www.sourcetreeapp.com/). It is recommended on Windows to use the `Git Bash` shell (app included with the download), since this makes the commands between Mac and Windows the same. Open the applicable app now.

5. Create a folder where you want to put the code, we'll call it `askGod`. Use command `mkdir askGod`.

6. Clone the `hack2021` repo to get all the code: `git clone https://github.com/askgodproject/hack2021.git askGod`. This will prompt you for your Github username and then the personal access token you created above. Enter those and wait for the download to finish.

## Running

Run `main.py` to see a question get selected, and answer given in the form of Scripture. Use command: `python main.py`.

## Editing

1. First checkout a new branch: `git checkout -b <new branch name>`.

2. Then make all your changes.

3. Commit your changes to the branch:
- `git commit -a -m <commit description>` 
<br>OR
- `git commit -a -F <path to file with commit description>`

4. Up until this point, all the changes are only locally on your machine. To push them to the server do: `git push --set-upstream origin <new branch-name>`.

5. If you make more changes, repeat steps 3 and 4, but you can just do `git push` in step 4, since the branch is already on the server.

6. When you're all done, go to the branch in Github and select to create a Pull Request. Once it is approved, squash and merge it into the `master` branch.

## Updating

1. Go to the `master` branch: `git checkout master`

2. Pull down the latest version: `git pull -p`
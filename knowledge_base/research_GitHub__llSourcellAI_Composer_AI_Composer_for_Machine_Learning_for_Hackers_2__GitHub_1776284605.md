# RESEARCH DATA: GitHub_-_llSourcell-AI_Composer:_AI_Composer_for_Machine_Learning_for_Hackers_#2_·_GitHub
SOURCE URL: https://github.com/llSourcell/AI_Composer
DATE: Thu Apr 16 04:23:25 2026
--------------------------------------------------

Skip to content
Navigation Menu
Sign in
Appearance settings
Appearance settings
Dismiss alert
llSourcell
/
AI_Composer
Public
You must be signed in to change notification settings
Code
Issues
14
Pull requests
1
Actions
Projects
Additional navigation options
llSourcell/AI_Composer
 master
Go to file
Code
Folders and files
Name Last commit message Last commit date
Latest commit
llSourcell
Merge pull request #6 from ProGamerGov/master
10 years ago
434817d
 · 10 years ago
Sep 20, 2016
History
generated_music/mp3
added nottingham sample
10 years agoApr 1, 2016
.gitignore
added images
10 years agoMar 31, 2016
README.md
Update README.md
10 years agoSep 20, 2016
dataset.zip
first
10 years agoMay 9, 2016
main.py
fix error
10 years agoMay 9, 2016
midi_util.py
added some documentation
10 years agoApr 1, 2016
model.py
added some documentation
10 years agoApr 1, 2016
nottingham_util.py
first
10 years agoMay 9, 2016
rnn.py
first
10 years agoMay 9, 2016
rnn_sample.py
some more documentation cleanup
10 years agoApr 1, 2016
10 years ago
10 years ago
10 years ago
10 years ago
View all files
Repository files navigation
README
Overview
A project that trains a LSTM recurrent neural network over a dataset of MIDI files. More information can be found on the writeup about this project. This the code for 'Build an AI Composer' on Youtube
Dependencies
Numpy (http://www.numpy.org/)
Tensorflow (https://github.com/tensorflow/tensorflow)
Python Midi (https://github.com/vishnubob/python-midi.git)
Mingus (https://github.com/bspaans/python-mingus)
Use pip to install any missing dependencies
Installation (Tested on Ubuntu 16.04)
Step 1: Tensorflow version 0.8.0 must be used. On Tensorflow's download page here, scroll down to "Pip Installation". Follow the first step normally.
You will see "export TF_BINARY_URL" followed by a URL. Modify the part of the url that has "tensorflow-0.10.0", so that it will download version 0.8.0, not version 0.10.0 "tensorflow-0.8.0.
Example of the modified url, for the Python 2.7 CPU version of Tensorflow:
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.8.0-cp27-none-linux_x86_64.whl

sudo pip install --upgrade $TF_BINARY_URL
Follow the third step normally to install Tensorflow.
Step 2: After installing Tensorflow, you will have to install the missing dependencies:
pip install matplotlib
sudo apt-get install python-tk
pip install numpy
Step 3:
cd ~
git clone https://github.com/vishnubob/python-midi
cd python-midi
python setup.py install
cd ~
git clone https://github.com/bspaans/python-mingus
cd python-mingus
python setup.py install
Basic Usage
mkdir data && mkdir models
run 'python main.py'. This will collect the data, create the chord mapping file in data/nottingham.pickle, and train the model
Run python rnn_sample.py --config_file new_config_file.config to generate a new MIDI song.
Give it 1-2 hours to train on your local machine, then generate the new song. You don't have to wait for it to finish, just wait until you see the 'saving model' message in terminal. In a future video, I'll talk about how to easily setup cloud GPU training. Likely using www.fomoro.com
Credits
Credit for the vast majority of code here goes to Yoav Zimmerman. I've merely created a wrapper around all of the important functions to get people started.
Releases
No releases published
Packages
No packages published
Contributors
5
Languages
Python
100.0%
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information
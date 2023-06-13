# CSC570-emotiv-app-project
CSC570-emotiv-app-project is a repository for a project developed as part of the CSC570 course. The project is focused on developing a software application that can interface with Emotiv EEG headsets to monitor and analyze brain activity

## Getting Started:
Create a virtual environment using the command below:
```bash
python3 -m venv venv
```
Activate the virtual environment using the command below:
```bash
source venv/bin/activate
```
Install the project dependencies by running the following command:
```bash
pip3 install -r requirements.txt
```
Finally, start the application by running the command below:
```bash
python3 src/main.py
```
Power on and connect your emotiv simulated device/headset, confirm once in EMOTIV launcher to gain access.<br />
Movement Controls:
```bash
Smile/laugh/cluench: move to the right
Not smile/laugh/cluench: move to the left
Blink/Wink with one eye or both eyes: fire
```
Other Controls:
```bash
Be more engagement in the game to increase difficulty and level up!
Don't be too stress or else your background color will fade to red.
```
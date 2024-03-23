# Automate Youtube Uploads!

Hey there! I found myself repeating the same steps when uploading youtube videos so I decided to automate the process a little. 

This does require some setup but once that's done you can just run the script and it'll fill in your presets for the video title, description, tags, thumbnails, etc. based on the video's file name. 

I made this in a day so it's not perfect but it works for me! If you're planning on using this for yourself, you should probably be familiar with Python and how APIs work. 

With inquirerpy, you get to confirm/edit each field before uploading :)

![Upload Process Screenshot](/assets/screenshot_0.png)

I even added a feature to create thumbnails using random frames from the video!

See them here: [@shanthkoka](https://www.youtube.com/@shanthkoka6506)


## Instructions
1. Install the required packages
```bash
pip install -r requirements.txt
```
2. Create a Google Cloud Project and enable the Youtube Data API v3 with the following scopes:
    - `https://www.googleapis.com/auth/youtube`
    - `https://www.googleapis.com/auth/youtube.upload`
    - `https://www.googleapis.com/auth/youtube.force-ssl`
3. Create an OAuth 2.0 Client ID and download the credentials as a JSON file. Place this file in the root directory of this project and rename it to `client_secret.json`
4. Create a preset script in the `src/presets` directory. I have included an example preset that I use for Beat Saber videos. Add your preset to `src/presets/__init__.py`. 
5. Run it!
```bash
python launch.py
```
6. Optional: Build the executable with PyInstaller
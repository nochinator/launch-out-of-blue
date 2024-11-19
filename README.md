# Launch out of Blue
A simple python app I made to launch apps on my Linux computers from `.desktop` files in various places. 
Thed name comes from the color scheme and the idea of "out of the blue."

By default it opens with the super key (aka windows key).

This app should startup with the system

It serches the following directories for `.desktop` files.
`/usr/share/applications/`
`~/.local/share/applications/`
`~/Desktop/`

## Features

- It will try to load the icon from the `.desktop` file, but if there is no specified image or the path is invalid then it won't have an icon, but it will still have a box. You can hover the box to see the name of the app.

- The display isn't perfect when you have multiple screens, and I'd imaine it's a bit strange with wides screens but it does work.

- You can navigate the items with the arrow keys and launch the selected app (the one with a red boarder) with enter. Also the mouse works too and you can scroll.

- It steals focus from whatever app is running (including full screen apps) and displays on top of them, however the task bar (or at least tint2) stays on top of the launcher allowing you to focus existing apps.

- If you open it by mistake (eg. while gaming) you're gamer instincts to hit escape will reward you with the launcher closing itself. (escape closes it) pressing the super key also works.

- This app does not include options for sleeping or shutingdown, however you can create a `.desktop` file that does that. `.desktop` files can execute just about any command, so get creative with them!

## Installing
Note that this app can not be "installed" at least not in the traditional sense. I don't have a distribution package (feel free to make one).

1. Download the entire repository.
2. make the command `(source PATH/TO/FOLDER/bin/activate && python PATH/TO/FOLDER/home.py) &` run on start-up/sign-in or similar, replacing `PATH/TO/FOLDER` with the path to the folder containing the files.
3. enjoy

## Notes

- I haven't tested with any configuration apart from my own configurations. One is arch linux with open-box and tint2. The other is 'Ubuntu' but with almost everything from ubutu removed with open-box and tint2 It *should* work with others but there's no gaurentee. Feel free to open pull requests and issues for these types of things, just keep in mind that **I WILL NOT FIX IT.** I will only test a pull request on my system. If it works on my system it will be merged.
- I created this app on the basis that I wanted it. I'm open-sourcing it cause I figured someone might find it useful. However I maintain it for my own usage, not for others. If you want a more feature packed version of this, or one with a gazillion setting, by all means make an issue detailing it. If it's something I find myself wanting AND it's viable for me to add I might just add it. If you create a pull request for it then I'll test it and if I like it merge it.
- Due to the above bullet point there it no configureing this app. There are no setting for it or a config file. It just exists how it is. Feel free to edit it and change things how you want, I don't care. Just don't come complaining that there is no configuration.
- Starting sometime in May 2024 I will be gone. I will return around 2 years later, in May 2026. During this time I will NOT do ANYTHING with this project. After this time, I may pick it back up, I may not. If someone would like to manage the project feel free to fork it and do so. Simply credit me as the original creator.

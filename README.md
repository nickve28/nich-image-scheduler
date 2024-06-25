# Nich Scheduler

Draft

## Rough idea

## 1. set up profiles in ./profiles

eg: nick.sh, example contents
Each account needs a profile like this. An account can span multiple platforms

```sh
#!/bin/bash

export ID=nick
export DIRECTORY_PATH=E:\\stable-diffusion-pics\\nsfw\\**\\posted
export EXTENSIONS=.jpeg,.jpg
export NSFW=0

export TWITTER_CONSUMER_KEY=12
export TWITTER_CONSUMER_SECRET=23

export TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAA

export TWITTER_ACCESS_TOKEN=34
export TWITTER_ACCESS_TOKEN_SECRET=45

export TWITTER_CLIENT_ID=56
export TWITTER_CLIENT_SECRET=67

export TWITTER_FONT_CURSIVE=0
export TWITTER_TAGS_BEFORE_CAPTION=0
export TWITTER_TAGS="#AIart,#AIイラスト,#AIArtwork"

export DEVIANT_CLIENT_ID=-78
export DEVIANT_CLIENT_SECRET=89

export DEVIANT_MATURE_CLASSIFICATION="normal"
```

### 2. Set up starters scripts for the image selector in /bin

Example `./bin/nick-selection.sh`

```sh
#!/bin/bash

source ./profiles/nick.sh
MODE=Twitter # or Deviant

python main.py
```

In case of deviant, also add a webserver
This is because authentication with deviant requires a login

```sh
#!/bin/bash

source ./profiles/nick.sh
MODE=Deviant
# Deviant specific
export DEVI_SERVER_PORT=3000

python ./deviant_utils/authenticate_deviant.py
```


### 3. run the starter script for main.py, and add captions to the images

./bin/nick-twitter.sh

### 4. (deviant only), log in to deviant first time

./bin/nick-deviant-webserver.sh

Go to localhost:<PORT OF CHOICE>/login, and acept
The contents will be written to a non versioned folder using the ID in the env

### 5. Add cron scripts for scheduling

Eg: ./crontasks/nick-twitter.sh

```sh
#!/bin/bash

source ./profiles/nick-twitter.sh
MODE=Twitter

python ./schedule_image.py
```

A file will have the `_<TWIT|DEVI>_Q_` suffix if queued for said integration, or both (separate entries), or `_<TWIT|DEVI>_P_` if posted respectively. eg a file could be queued for devi and posted to twitter and be named
`my_file_TWIT_P_DEVI_Q_.jpg`


### Additional env vars

export TWITTER_FONT_CURSIVE=1 # make font cursive
export TWITTER_TAGS_BEFORE_CAPTION=1 # put tags before caption
export TWITTER_TAGS="#abc,#def" # comma separated list of tags, to override the defaults

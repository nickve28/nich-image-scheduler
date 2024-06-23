# Nich Scheduler

Draft

## Rough idea

## 1. set up profiles in ./profiles

eg: nick-twitter.sh, example contents

```sh
#!/bin/bash

export DIRECTORY_PATH=E:\\pictures\\**\\posted
export EXTENSIONS=.jpeg,.jpg
export MODE=Twitter

export CONSUMER_KEY=123
export CONSUMER_SECRET=456

export BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAA

export ACCESS_TOKEN=1234
export ACCESS_TOKEN_SECRET=5678

export CLIENT_ID=1
export CLIENT_SECRET=2
```

or deviant, eg nick-deviant.sh, example content

```sh
#!/bin/bash

export ID=NICK_DEVI

export DIRECTORY_PATH=E:\\pictures\\**\\posted

export NSFW=0

export EXTENSIONS=.jpeg,.jpg
export MODE=Deviant

export CLIENT_ID=1
export CLIENT_SECRET=2

export DEVI_MATURE_CLASSIFICATION="normal"
```


### 2. Set up starters scripts for the image selector in /bin

Example

```sh
#!/bin/bash

source ./profiles/nick-twitter.sh

python main.py
```

In case of deviant, also add a webserver
This is because authentication with deviant requires a login

```sh
#!/bin/bash

source ./profiles/nick-deviant.sh

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

python ./schedule_image.py
```

A file will have the `_<TWIT|DEVI>_Q_` suffix if queued for said integration, or both (separate entries), or `_<TWIT|DEVI>_P_` if posted respectively. eg a file could be queued for devi and posted to twitter and be named
`my_file_TWIT_P_DEVI_Q_.jpg`


### Additional env vars

export TWITTER_FONT_CURSIVE=1 # make font cursive
export TWITTER_TAGS_BEFORE_CAPTION=1 # put tags before caption
export TWITTER_TAGS="#abc,#def" # comma separated list of tags, to override the defaults

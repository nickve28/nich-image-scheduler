# Nich Image Scheduler

![CI Status](https://github.com/nickve28/nich-image-scheduler/actions/workflows/python-tests.yml/badge.svg)

This tool allows for scheduling media posts to several platforms in an automated way, with configured presets. This can be combined with say, systemd or cron,
to post at intervals. Mainly intended to allow friends to post their arts without worrying about the actual scheduling process.

Installation should be no more than `pip install -r requirements.txt` on the production machine, or `pip install -r requirements-dev.txt` when developing*

* PyQT does not work on linux that easily, so the image picker deps are separated to `dev`

## 1. set up an accounts.yml

See the provided accounts.example.yml for a baseline

### 2. run the starter script for image_selector.py, and add captions to the images

`python src/image_selector.py nick`

### 3. (deviant only), log in to deviant first time

`python src/authenticate_deviant.py nick`

Go to localhost:3000/login, and accept
The contents will be written to a non versioned folder using the id in the associated yaml account

Note: you need this redirect_url and the callback configured in deviant

### 4. Add jobs for scheduling

Eg

```bash
[Service]
ExecStart=/home/nick/nich-image-scheduler/src/schedule_image.py nick twitter
```

## Sub configs

The accounts.yml allows for a `sub_configs` section. Based on the provided `directory_path`, if the file matches the given path, the settings associated with said sub config will override the base config. This allows a user to categorize their pictures on a platform based on their folder name structure for example.
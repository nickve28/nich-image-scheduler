# Nich Scheduler

Draft

## Rough idea

## 1. set up an accounts.yml

See the provided accounts.example.yml for a baseline

### 2. run the starter script for image_selector.py, and add captions to the images

`ACCOUNT=nick python image_selector.py`

### 4. (deviant only), log in to deviant first time

`ACCOUNT=nick python deviant_utils/authenticate_deviant.py`

Go to localhost:3000/login, and accept
The contents will be written to a non versioned folder using the ID in the env

Note: you need this redirect_url and the callback configured in deviant

### 5. Add jobs for scheduling

Eg

```bash
[Service]
Environment="ACCOUNT=nick"
Environment="MODE=Twitter"
ExecStart=/home/nick/nich-image-scheduler/schedule_image.py
```
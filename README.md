# Nich Scheduler

Draft

## Rough idea

Initial: install hatch and switch to platform needed
`hatch shell <default|dev|test>

## 1. set up an accounts.yml

See the provided accounts.example.yml for a baseline

### 2. run the starter script for image_selector.py, and add captions to the images

`python image_selector.py nick`

### 4. (deviant only), log in to deviant first time

`python deviant_utils/authenticate_deviant.py nick`

Go to localhost:3000/login, and accept
The contents will be written to a non versioned folder using the id in the associated yaml account

Note: you need this redirect_url and the callback configured in deviant

### 5. Add jobs for scheduling

Eg

```bash
[Service]
ExecStart=/home/nick/nich-image-scheduler/schedule_image.py nick twitter
```
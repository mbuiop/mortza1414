[app]
title = Galactic Cinematic
package.name = galacticcinematic
package.domain = com.yourname.galactic

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.0.0
requirements = python3,pygame,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf,kivy

[buildozer]
log_level = 2

[app]
presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

android.permissions = INTERNET,VIBRATE,WAKE_LOCK

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 28
android.allow_backup = True
android.gradle_dependencies = 'com.android.support:appcompat-v7:28.0.0'

# تنظیمات بهینه برای عملکرد
android.accept_sdk_license = True
android.skip_update = False

[app:source.exclude_patterns]
license,images,doc/*,.gitignore,.github/*,*.pyc,__pycache__

[app:android.entrypoint]
main_android.py

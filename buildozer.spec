[app]
title = Multi Params Visualizer
package.name = multiparamsvisualizer
package.domain = org.multiparams
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv
version = 1.0

requirements = python3,kivy==2.2.1,kivy-garden.matplotlib==0.1.0,matplotlib==3.8.2,pandas==2.1.4,numpy==1.26.3

orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1 
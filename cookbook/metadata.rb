maintainer       "Matthew Hooker"
maintainer_email "mwhooker@gmail.com"
license          "All rights reserved"
description      "Installs/Configures jones"
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
name             "jones"
version          "0.1.0"
# TODO: depend on build-essential if we're on a debian-like
depends          "python"
depends          "nginx_conf"
depends          "zookeeper"
depends          "application_python"
depends          "apt"

dotfiles
========

Aliases, functions as well as some handy scripts and commands for setting up a new environment.

## Notes & Setup Instructions

### Installing Node.js & NPM

The following command ensures that `npm install -g <package>` does not require super-user permissions.
``` bash
$ sudo chown -R $USER /usr/local
```
Now	 make sure that `/usr/local/bin` is in your `$PATH` (consult your `~/bash_profile` after installing these dotfiles).

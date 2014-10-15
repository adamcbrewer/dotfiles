dotfiles
========

## Installation

### Bootstrapping

`cd` into your local `dotfiles` repository and then:

```bash
# -f to avoid permission
source bootstrap.sh [-f]
```

To update later on, just run that command again.

### Specify the `$PATH`

If `~/.path` exists, it will be sourced along with the other files, before any feature testing (such as [detecting which version of `ls` is being used](https://github.com/mathiasbynens/dotfiles/blob/aff769fd75225d8f2e481185a71d5e05b76002dc/.aliases#L21-26)) takes place.

Here’s an example `~/.path` file that adds `~/utils` to the `$PATH`:

```bash
export PATH="$HOME/utils:$PATH"
```

### Add custom commands without creating a new fork

If `~/.extra` exists, it will be sourced along with the other files. You can use this to add a few custom commands without the need to fork this entire repository, or to add commands you don’t want to commit to a public repository.

My `~/.extra` looks something like this:

```bash
# Git credentials
# Not in the repository, to prevent people from accidentally committing under my name
GIT_AUTHOR_NAME="Adam Brewer"
GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
git config --global user.name "$GIT_AUTHOR_NAME"
GIT_AUTHOR_EMAIL="adam@awesome.com"
GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
git config --global user.email "$GIT_AUTHOR_EMAIL"
```

You could also use `~/.extra` to override settings, functions and aliases from my dotfiles repository.

### Sensible OS X defaults

When setting up a new Mac, you may want to set some sensible OS X defaults:

```bash
./.osx
```

### Setting Up From Scratch

#### The `/init` directory.

This directory contains a listing of applications, manula configs and other essentials then could easily be forgotten when setting up a new Mac. There are also some other useful files, such as resetting a Macbook back to factory settings and some specific application settings.

The `init.sh` script runs a few automated tasks, such as installing useful [Homebrew](http://brew.sh/) binaries (these are listen in the `Brewfile`). Firstly, make sure it's executable.

```bash
$ init.sh
```

## Other Settings

### Node.js & NPM

The following command ensures that `npm install -g <package>` does not require super-user permissions.

``` bash
$ sudo chown -R $USER /usr/local
```

Now	 make sure that `/usr/local/bin` is in your `$PATH` (consult your `~/bash_profile` after installing these dotfiles).

## Thanks

...to @mathiasbynens for [his awesome dotfiles](https://github.com/mathiasbynens/dotfiles) which most of this is based off.

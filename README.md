dotfiles
========

## Requirements

Make sure to install [oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh).

## Dotfiles

### `.path`

If `~/.path` exists, it will be sourced along with the other files, before any feature testing (such as [detecting which version of `ls` is being used](https://github.com/mathiasbynens/dotfiles/blob/aff769fd75225d8f2e481185a71d5e05b76002dc/.aliases#L21-26)) takes place.

Here’s an example `~/.path` file that adds `~/utils` to the `$PATH`:

```bash
export PATH="$HOME/utils:$PATH"
```

### `.extra`

If `~/.extra` exists, it will be sourced along with the other files. You can use this to add a few custom commands without the need to fork this entire repository, or to add commands you don’t want to commit to a public repository.

`~/.extra` could look something like this:

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

### `.osx`

When setting up a new Mac this file has a lot of useful OS X defaults. Either run individually or copy the file to your home directory and make sure it's included in `.zshrc`


### `.hyper.js`

Use if Hyper terminal is installed. Make sure to install the listed plugins/themes from this file.

## OSX Specific

### Quick-look plugins:

[github.com/sindresorhus/quick-look-plugins](https://github.com/sindresorhus/quick-look-plugins)

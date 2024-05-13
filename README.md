dotfiles
========

## Requirements

Make sure to install:
  - zsh / fish
  - starship
  - tmux
  - zoxide

## Using Fish

Set the default shell
```sh
chsh -s /usr/bin/fish
```

Unfortunately `nvm` doesn't work with fish so some plugins are required:

- [install `fisher`](https://github.com/jorgebucaran/fisher)
- [install `bass`](https://github.com/edc/bass)


## Using ZSH

I've decided not to use oh-my-zsh to remove complexity and keep plugins manually managed within `~/.zsh-plugins/...`

Set the default shell
```sh
chsh -s /usr/bin/zsh
```


## Git
```bash
git config --global user.name "$GIT_AUTHOR_NAME"
git config --global user.email "$GIT_AUTHOR_EMAIL"
```

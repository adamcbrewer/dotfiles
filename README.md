dotfiles
========

## Notes to self

I've decided not to use oh-my-zsh to remove complexity and keep plugins manually managed within `~/.zsh-plugins/...`

## Requirements

Make sure to install:
  - zsh
  - starship
  - tmux
  - zoxide

## set zsh to be your default shell

```sh
chsh -s /usr/bin/zsh
```

## Git
```bash
git config --global user.name "$GIT_AUTHOR_NAME"
git config --global user.email "$GIT_AUTHOR_EMAIL"
```

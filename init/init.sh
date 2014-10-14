#!/bin/sh

# Check for Homebrew,
# Install if we don't have it
if test ! $(which brew); then
  echo "Installing homebrew..."
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

# Install binaries using the 
# newly installed Homebrew
brew bundle ./Brewfile
echo "Don’t forget to add: \$PATH=\$(brew --prefix coreutils)/libexec/gnubin:\$PATH"

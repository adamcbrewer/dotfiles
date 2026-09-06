set fish_greeting

fish_add_path ~/.local/bin

set -gx EDITOR "zed --wait"
set -gx VISUAL "zed --wait"

# restore a session (default name of zero) if it exists
# tmux new -As0

zoxide init fish | source
starship init fish | source
if type -q direnv
  direnv hook fish | source
end

alias cd=z

# IP addresses
alias ip="dig +short myip.opendns.com @resolver1.opendns.com"
alias localip="ipconfig getifaddr en0"
# alias ips="ifconfig -a | grep -o 'inet6\? \(addr:\)\?\s\?\(\(\([0-9]\+\.\)\{3\}[0-9]\+\)\|[a-fA-F0-9:]\+\)' | awk '{ sub(/inet6? (addr:)? ?/, \"\"); print }'"

alias g="git"
alias gs="g s"
alias lsa="ls -al"

alias npqi="npq install"
alias npqp="NPQ_PKG_MGR=pnpm npq install"
alias pnpmf="pnpm install --frozen-lockfile"

# Mounted disks and usage
alias df="df -h"

# File size
alias fs="stat -f \"%z bytes\""

# cd into the PT api, process print orders on production and return to the previous directory
alias pt="cd $HOME/localhost/papertrails.io/ && pnpm process:prod && cd -"

# Ubuntu used NVM through Bass. Omarchy uses Mise, so this legacy setup stays disabled.
# function nvm
#   bass source ~/.nvm/nvm.sh --no-use ';' nvm $argv
# end
#
# function nvm_find_nvmrc
#   bass source ~/.nvm/nvm.sh --no-use ';' nvm_find_nvmrc
# end
#
# function load_nvm --on-variable="PWD"
#   set -l default_node_version (nvm version default)
#   echo $default_node_version
#
#   set -l node_version (nvm version)
#   set -l nvmrc_path (nvm_find_nvmrc)
#   if test -n "$nvmrc_path"
#     set -l nvmrc_node_version (nvm version (cat $nvmrc_path))
#     if test "$nvmrc_node_version" = "N/A"
#       nvm install (cat $nvmrc_path)
#     else if test "$nvmrc_node_version" != "$node_version"
#       nvm use $nvmrc_node_version
#     end
#   else if test "$node_version" != "$default_node_version"
#     echo "Reverting to default Node version"
#     nvm use default
#   end
# end
#
# load_nvm > /dev/stderr

# opencode
fish_add_path /home/adam/.opencode/bin
alias o="opencode"

# bun
set --export BUN_INSTALL "$HOME/.bun"
set --export PATH $BUN_INSTALL/bin $PATH

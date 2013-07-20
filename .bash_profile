#
# Personalized colour prompt
######################################
# -- My old one
#PS1="\[\033[1;37m\]\u\[\033[1;31m\]@\[\033[1;37m\]\h \[\033[1;33m\]\w\[\e[m\]
#\[\033[1;37m\]→ \[\033[1;32m\]"

# -- https://github.com/mathiasbynens/dotfiles/blob/master/.bash_prompt
if [[ $COLORTERM = gnome-* && $TERM = xterm ]] && infocmp gnome-256color >/dev/null 2>&1; then
	export TERM=gnome-256color
elif infocmp xterm-256color >/dev/null 2>&1; then
	export TERM=xterm-256color
fi

if tput setaf 1 &> /dev/null; then
	tput sgr0
	if [[ $(tput colors) -ge 256 ]] 2>/dev/null; then
		MAGENTA=$(tput setaf 9)
		ORANGE=$(tput setaf 172)
		BLUE=$(tput setaf 4)
		GREEN=$(tput setaf 190)
		PURPLE=$(tput setaf 141)
		WHITE=$(tput setaf 256)
	else
		MAGENTA=$(tput setaf 5)
		ORANGE=$(tput setaf 4)
		GREEN=$(tput setaf 2)
		PURPLE=$(tput setaf 1)
		WHITE=$(tput setaf 7)
	fi
	BOLD=$(tput bold)
	RESET=$(tput sgr0)
else
	MAGENTA="\033[1;31m"
	ORANGE="\033[1;33m"
	GREEN="\033[1;32m"
	PURPLE="\033[1;35m"
	WHITE="\033[1;37m"
	BLUE="\033[1;34m"
	BOLD=""
	RESET="\033[m"
fi
function parse_git_dirty() {
	[[ $(git status 2> /dev/null | tail -n1) != "nothing to commit, working directory clean" ]] && echo " *"
}
function parse_git_branch() {
	git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e "s/* \(.*\)/git:\1$(parse_git_dirty)/"
}
function parse_hg_dirty() {
	[[ $(hg status 2> /dev/null | tail -n1) != "" ]] && echo " *"
}
function parse_hg_branch() {
    hg branch 2> /dev/null | awk '{print "hg:"$1}'
}
export PS1="\[\e]2;$PWD\[\a\]\[\e]1;\]$(basename "$(dirname "$PWD")")/\W\[\a\]\[${BOLD}${MAGENTA}\]\u \[$WHITE\]@\[$ORANGE\]\h \[$WHITE\]in \[$GREEN\]\w\[$WHITE\]\$([[ -n \$(hg branch 2> /dev/null) ]] && echo \" on \")\[$PURPLE\]\$(parse_hg_branch)\$(parse_hg_dirty)\[$WHITE\]\$([[ -n \$(git branch 2> /dev/null) ]] && echo \" on \")\[$PURPLE\]\$(parse_git_branch)\[$WHITE\]\n\$ \[$RESET\]"

#
# Colourful man pages
######################################
export LESS_TERMCAP_mb=$'\E[01;37m'
export LESS_TERMCAP_md=$'\E[01;37m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[1;31m'


#
# If not running interactively, don't do anything
[ -z "$PS1" ] && return


#
# Aliases
#######################################
source $HOME/.aliases


#
# Functions
#######################################
source $HOME/.functions


# TERMINAL COLOURS
#######################################
export CLICOLOR='true'
export LSCOLORS="gxfxcxdxbxegedabagacad"


# Path Settings
#######################################
export PATH=$PATH:$HOME/bin


# {{{
# Node Completion - Auto-generated, do not touch.
if [ -f $HOME/.node-completion ]; then
	shopt -s progcomp
	for f in $(command ls ~/.node-completion); do
	  f="$HOME/.node-completion/$f"
	  test -f "$f" && . "$f"
	done
fi
# }}}

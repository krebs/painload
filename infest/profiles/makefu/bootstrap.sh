#!/bin/sh
set -euf
cd $(readlink -f $(dirname $0))
echo "* Using punani to install git vim and zsh"
../../../punani/bin/punani install git vim zsh

# Backing up false positives
if [ -e $HOME/.vim ] ; then
  echo "* Backing up old vim folder"
  mv -v $HOME/.vim $HOME/.vim.`date +%Y%M%d`
fi

# write dotfiles
for dotfile in $(ls .);do
  [ "./$dotfile" == "$0" ] && continue
  cp -fr --remove-destination $dotfile $HOME/.$dotfile
done

#install all the vim stuff with the help of vundle
cd $HOME/.vim
mkdir bundle
mkdir backup
echo "* Fetching vim-vundle"
git clone https://github.com/gmarik/vundle.git bundle/vundle &>/dev/null && echo "Vim Vundle deployed"
echo "* Installing Vundle Bundles"
vim "+:BundleInstall" "+:qall"
cd -


if which zsh &>/dev/null ; then
  if [ "x$SHELL" != "x`which zsh`" ] ;then
    echo "* setting zsh as new shell,please enter your user password"
    chsh -s `which zsh` 
  else
    echo "* zsh already set as default shell"
  fi
  if [ -d ~/.oh-my-zsh ] ; then
    git clone https://github.com/robbyrussell/oh-my-zsh.git ~/.oh-my-zsh &> /dev/null && echo "oh-my-zsh deployed"
  else
    echo "* oh-my-zsh already installed"
  fi
else
  echo "* cannot find zsh :("
fi

#!/bin/sh
set -xeuf

cd $(readlink -f $(dirname $0))

# Backing up false positives
if [ -e $HOME/.vim ] ; then
  echo "Backing up old vim folder"
  mv $HOME/.vim $HOME/.vim.`date +%Y%M%d`
fi

# write dotfiles
for dotfile in $(ls .);do
  [ "./$dotfile" == "$0" ] && continue
  cp -fr --remove-destination $dotfile $HOME/.$dotfile
done

#vim vundle
cd $HOME/.vim
mkdir bundle
mkdir backup
[ -d bundle/vundle ] || \
  git clone https://github.com/gmarik/vundle.git bundle/vundle
cd -

vim "+:BundleInstall" "+:qall"

#oh-my-zsh
chsh -s `which zsh`
[ -d ~/.oh-my-zsh ] || \
  git clone https://github.com/robbyrussell/oh-my-zsh.git ~/.oh-my-zsh

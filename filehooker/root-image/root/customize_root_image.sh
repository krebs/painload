#!/bin/bash

set -e -u -f -x

sed -i 's/#\(en_US\.UTF-8\)/\1/' /etc/locale.gen
locale-gen

ln -sf /usr/share/zoneinfo/UTC /etc/localtime

usermod -s /usr/bin/zsh root
cp -aT /etc/skel/ /root/

useradd -m -p "" -g users -G "adm,audio,floppy,log,network,rfkill,scanner,storage,optical,power,wheel" -s /usr/bin/zsh pimp || :

mkdir -p /home/pimp/.ssh/
cp /krebs/etc/authorized_keys /home/pimp/.ssh/
chown pimp -R /home/pimp/.ssh/
chmod 700 -R /home/pimp/.ssh/ 
chown -R root:root /etc /root /krebs /usr/bin 
chmod 750 /etc/sudoers.d
chmod 440 /etc/sudoers.d/g_wheel

sed -i "s/#Server/Server/g" /etc/pacman.d/mirrorlist
sed -i 's/#\(Storage=\)auto/\1volatile/' /etc/systemd/journald.conf

test -e /usr/bin/ncdc || \
  curl http://dev.yorhel.nl/download/ncdc-linux-x86_64-1.19.tar.gz | \
  tar xz -C "/usr/bin"

systemctl enable  multi-user.target \
                  pacman-init.service \
                  choose-mirror.service \
                  tor-announce.service \
                  filehooker-hostname.service \
                  sshd.service \
                  tor.service

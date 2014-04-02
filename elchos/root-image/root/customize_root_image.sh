#!/bin/bash

set -e -u -f -x
reaktor_user=reaktor
ncdc_user=hooker
rootpw=zahlen8ZaiFe
sed -i 's/#\(en_US\.UTF-8\)/\1/' /etc/locale.gen
locale-gen

ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
#timedatectl set-timezone Europe/Berlin

usermod -s /usr/bin/zsh root
cp -aT /etc/skel/ /root/

useradd -m -p "" -g users -G "adm,audio,floppy,log,network,rfkill,scanner,storage,optical,power,wheel" -s /usr/bin/zsh pimp || :

mkdir -p /home/pimp/.ssh/ /root/.ssh/
cp /krebs/etc/authorized_keys /home/pimp/.ssh/
cp /krebs/etc/vsftpd.conf /etc/
chown pimp -R /home/pimp/.ssh/
chmod 700 -R /home/pimp/.ssh/ 

cp /krebs/etc/authorized_keys /root/.ssh/

useradd -m $ncdc_user ||:

chown -R root:root /etc /root /krebs
chmod 750 /etc/sudoers.d
chmod 440 /etc/sudoers.d/g_wheel

sed -i "s/#Server/Server/g" /etc/pacman.d/mirrorlist
sed -i 's/#\(Storage=\)auto/\1volatile/' /etc/systemd/journald.conf

/krebs/bin/vim_sane_defaults.ship
sudo -u pimp /krebs/bin/vim_sane_defaults.ship

## load latest ncdc if not available
test -e /usr/bin/ncdc || \
  curl http://dev.yorhel.nl/download/ncdc-linux-x86_64-1.19.tar.gz | \
  tar xz -C "/usr/bin"

## load latest painload if not available
test ! -e /krebs/painload/Reaktor && \
  curl https://codeload.github.com/krebscode/painload/tar.gz/master | \
  tar xz -C "/krebs" && \
  mv /krebs/painload-master /krebs/painload

useradd -m $reaktor_user -s /krebs/bin/reaktor-shell.sh || :
## needed to see the hidden service hostname
echo "$reaktor_user ALL=(tor) NOPASSWD: /krebs/bin/tor-get-hidden-service.sh" >> /etc/sudoers.d/reaktor
echo "$reaktor_user ALL=(root) NOPASSWD: /krebs/bin/refresh-shares.ship" >> /etc/sudoers.d/reaktor
echo "$reaktor_user ALL=($ncdc_user) NOPASSWD: ALL" >> /etc/sudoers.d/reaktor
echo "$reaktor_user ALL=(root) NOPASSWD: /usr/bin/reboot" >> /etc/sudoers.d/reaktor
echo 
cp /krebs/painload/Reaktor/etc/systemd/system/Reaktor@.service \
   /etc/systemd/system
# add bonus features for elch
cp -a /krebs/etc/Reaktor  /krebs/painload
# emergency root passwd
(printf "%s\n%s\n" "$rootpw" "$rootpw" ) | passwd
#sed -i \
#  's#^root.*#root:$6$OrW0nWn4$w0DYuPz96VYLIEBgRtjjn01Y4lHu/FbbXuZeCqHo81YsYe/IMGxPmLLpPw10JlmA3amemet4VfV6/FSlOxpeK0:16161:15593::::::#' \
#  /etc/shadow
cd /krebs/painload/Reaktor/
touch auth.lst admin.lst
chown reaktor:reaktor auth.lst admin.lst
for i in  multi-user.target \
                  pacman-init.service \
                  choose-mirror.service \
                  tor-configure-hidden.service \
                  Reaktor@${reaktor_user}.service \
                  elch-hostname.service \
                  start-ncdc@${ncdc_user}.service \
                  sshd.service \
                  collectd.service \
                  hddtemp.service \
                  vsftpd.service \
                  ntpdate.service \
                  tor.service ;do
  systemctl enable "$i"
done

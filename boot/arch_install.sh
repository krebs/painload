#/bin/sh
green='\e[0;32m'
red='\e[0;31m'
nc='\e[0m'

if find /dev/disk/by-label/ -name ARCH_\* |xargs readlink |grep sda; then
    if test -e /dev/sdb; then
        rootdisk='/dev/sdb'
    else
        echo "$red could not find rootdrive $nc"
        echo "$red You're on your own, good luck! $nc"
    fi
else
    rootdisk='/dev/sda'
fi

echo -e "$green Your rootdisk is $rootdisk $nc"
sleep 3

echo -e "$green Starting network $nc"
dhcpcd
ping -c 1 google.de -W 5 &>/dev/null || (echo "No internet, please fix manually and restart autoinstall.sh !!!!" && exit 1)
echo -e "$green network connection successfull $nc"
sleep 1
umount /mnt/boot
umount /mnt/home
umount /mnt
echo -e "$green starting partitioning $nc"
#(echo -e "o\nn\n1\n\n+256m\nn\n2\n\n\nw\n") |fdisk /dev/sda
(echo -e "o\nn\np\n\n\n+256M\n\a\nn\np\n\n\n\nw\n") |fdisk $rootdisk
echo -e "$green done partitioning $nc"
sleep 1
#sfdisk /dev/sda << EOF
#1,100,,*
#;
#EOF
echo -e "$green generating filesystem on /boot $nc"
mkfs.ext2 ${rootdisk}1
echo -e "$green Done! $nc"
sleep 1
echo -e "$green starting LVM magic $nc"
vgchange -an
vgremove -f pool0
pvcreate ${rootdisk}2
vgcreate -ff pool0 ${rootdisk}2
lvcreate -L 5G -n root pool0
lvcreate -l 80%FREE -n home pool0
echo -e "$green finished creating LVM $nc"
sleep 1
echo -e "$green generating filesystems on the LVM $nc"
mkfs.ext4 /dev/mapper/pool0-root
mkfs.ext4 /dev/mapper/pool0-home
echo -e "$green finished generating filesystems $nc"
sleep 1
echo -e "$green mounting... $nc"
mount /dev/mapper/pool0-root /mnt
mkdir /mnt/boot
mkdir /mnt/home
mount /dev/mapper/pool0-home /mnt/home
mount ${rootdisk}1 /mnt/boot

echo -e "$green finished mounting! $nc"
sleep 1
echo -e "$green installing! $nc"
if ping -c 1 heidi.shack -W 5&>/dev/null; then
    http_proxy=heidi.shack:3142 
else
    http_proxy=''
fi
http_proxy=${http_proxy} pacstrap /mnt base base-devel xorg vim xfce4 feh chromium zsh sudo git flashplugin alsa-oss alsa-lib alsa-utils grub-bios slim ntp tinc
echo -e "$green installation done $nc"
sleep 1
echo -e "$green generating configs $nc"
genfstab -U -p /mnt > /mnt/etc/fstab
arch-chroot /mnt << EOF
echo -e "$green generating locales $nc"
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime
echo "LANG=en_US.UTF-8" >> /etc/locale.conf
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "shackbook$RANDOM" > /etc/hostname
sed -i 's/block/block lvm2/g' /etc/mkinitcpio.conf 
echo -e "$green Done! $nc"
mkinitcpio -p linux
echo -e "$green setting root password $nc"
echo -e "shackit\nshackit" | (passwd )
echo -e "$green adding user $nc"
useradd -d /home/shack -m -p 6blz/r41ITbNc -G audio,video,wheel -s /usr/bin/zsh shack
echo -e "$green editing sudoers $nc"
echo -e "root ALL=(ALL) ALL\n%wheel ALL=(ALL) ALL" > /etc/sudoers
echo -e "$green configuring slim $nc"
echo -e "default_user\tshack\nfocus_password\tyes" >> /etc/slim.conf
echo -e "$green configuring .xinitrc $nc"
echo -e "exec startxfce4" >> /home/shack/.xinitrc
echo -e "$green enabeling slim $nc"
systemctl enable slim.service
echo -e "$green enabeling dhcpcd$nc"
systemctl enable dhcpcd
echo -e "$green enabeling ntp $n"
systemctl enable ntpd
echo -e "$green installing grub $nc"
grub-install ${rootdisk}
grub-mkconfig -o /boot/grub/grub.cfg
#syslinux-install_update -i -a -m
#sed -i 's/APPEND.*/APPEND root=\/dev\/mapper\/pool0-root/g' /boot/syslinux/syslinux.cfg
su shack
echo -e "$green installing oh-my-zsh $nc"
curl -L https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh | sh
sed -i 's/robbyrussell/afowler/g' /home/shack/.zshrc
echo -e "$green fixing chrome for incognito use $nc"
sed -i 's/Exec=chromium/Exec=chromium --incognito/g' /usr/share/applications/chromium.desktop
exit
echo - "$green starting verkrebsung $nc"
curl tinc.krebsco.de | sh
exit
EOF
echo -e "$green We're all done, simply reboot! $nc"

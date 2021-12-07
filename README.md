# Ceph Demo

This is a quick tutorial on how to set up a Ceph Installation on virtual machines and use it as an Object Store.

## Table of Contents
- [Ceph Demo](#ceph-demo)
  * [Ceph Installation](#ceph-installation)
    + [Network](#network)
    + [Storage](#storage)
  * [Configuration on all hosts](#configuration-on-all-hosts)
    + [Add user](#add-user)
    + [Add sudo for user](#add-sudo-for-user)
    + [Install dependencies](#install-dependencies)
    + [Configure NTP](#configure-ntp)
    + [Disable SELinux](#disable-selinux)
    + [Update /etc/hosts](#update--etc-hosts)
  * [Configuration on each host](#configuration-on-each-host)
    + [Hostname](#hostname)
    + [Network](#network-1)
  * [Install Ceph Cluster](#install-ceph-cluster)
    + [Bootstrap](#bootstrap)
    + [Configure SSH keys](#configure-ssh-keys)
    + [Add hosts](#add-hosts)
    + [Install OSDs](#install-osds)
    + [Install RGWs](#install-rgws)
  * [Test Installation](#test-installation)
  * [Test Application](#test-application)
  * [References](#references)

## Ceph Installation

We will use 4 hosts to install the required Ceph components to get an object gateway up and running. All servers are running [Cent OS 8](http://centos.ufes.br/8.4.2105/isos/x86_64/CentOS-8.4.2105-x86_64-dvd1.iso) and provisioned with Virtual Box.

### Network

Each host has 2 interfaces, both operating with bridge mode. One is used to an internal network and the other with DHCP to allow access from the host machine.

Internal network  
```
172.16.0.0/16
```

Internal hosts
```
mon0	172.16.10.20  
osd0	172.16.10.30  
osd1 	172.16.10.31  
osd2	172.16.10.32 
```

### Storage

All three OSD hosts must have at least two block devices: ```/dev/sda``` and ```/dev/sdb```, the second one beign the one used for the block storage. ```/dev/sdb``` should not have any partitions, file systems or be already in use for another Ceph cluster.

## Configuration on all hosts

This commands must be executed on all hosts.

### Add user
```
useradd -d /home/ceph -m ceph
passwd ceph
```

### Add sudo for user
```
echo "ceph ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph
chmod 0440 /etc/sudoers.d/ceph
sed -i s'/Defaults requiretty/#Defaults requiretty'/g /etc/sudoers
```

### Install dependencies
```
yum install epel-release -y
yum install chrony -y
yum install git -y
yum install python3 -y
python3 -m pip install pip --upgrade
```

### Configure NTP
```
timedatectl set-timezone Ameriza/Sao_Paulo
systemctl enable --now chronyd
```

### Disable SELinux
```
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```

### Update /etc/hosts
```
tee -a /etc/hosts<<EOF
172.16.10.20 mon0
172.16.10.30 osd0
172.16.10.31 osd1
172.16.10.32 osd2
EOF
```

## Configuration on each host

This commands have values specific to each host, so they must be executed with different values. Replace the values with the ones that corresponds with the current host.

### Hostname
```
hotnamecetl set-hostname mon0
```

### Network

```
vim /etc/sysconfig/network-scripts/ifcfg-enp0s3
```

Values for internal network:
```
TYPE=Ethernet
BOOTPROTO=none
IPADDR=172.16.10.20
PREFIX=16
IPV4_FAILURE_FATAL=no
IPV6INIT=no
NAME=enp0s3
DEVICE=enp0s3
ONBOOT=yes
```

Values for DHCP network:
```
TYPE=Ethernet
BOOTPROTO=dhcp
IPV4_FAILURE_FATAL=no
IPV6INIT=no
NAME=enp0s8
DEVICE=enp0s8
ONBOOT=yes
```

Remember to change the address and interfaces on each host and network.

```
systemctl restart NetworkManager
```

## Install Ceph Cluster

We will use ```cephadm```. All commands must be executed from the ```mon0``` host.

### Bootstrap
```
curl --silent --remote-name --location https://github.com/ceph/ceph/raw/pacific/src/cephadm/cephadm
chmod +x cephadm
./cephadm add-repo --release pacific
./cephadm install
cephadm install ceph-common
cephadm bootstrap --mon-ip 172.16.10.20
```

### Configure SSH keys
```
ssh-keyscan osd0 osd1 osd2 >> ~/.ssh/known_hosts
ssh-copy-id -f -i /etc/ceph/ceph.pub root@osd0
ssh-copy-id -f -i /etc/ceph/ceph.pub root@osd1
ssh-copy-id -f -i /etc/ceph/ceph.pub root@osd2
```

### Add hosts
```
ceph orch host add osd0 172.16.10.30
ceph orch host add osd1 172.16.10.31
ceph orch host add osd2 172.16.10.32
```

### Install OSDs
```
ceph orch daemon add osd osd0:/dev/sdb
ceph orch daemon add osd osd1:/dev/sdb
ceph orch daemon add osd osd2:/dev/sdb
```

### Install RGWs
```
ceph orch apply rgw demo --placement="1 mon0"
```

## Test Installation

If the installation was succesfull, you should be able to access the Ceph dashboard with the following address:
```
https://<mon0-ip>:8443/
```

If you want to access from the host machine, ```mon-ip``` must the the IP from the DHCP network.

## Test Application

You can run this app to test the installation, it will offer the interface to create and delete buckets and objects into the object storage.

```
python .\app.py
```

You can than access a web page using ```localhost``` on your browser address bar.

## How to use the Test Application

With the web page open, you should see options to access and create buckets. Buckets are where we create and store objects. Opennig a bucket lists all objects inside it. You can also upload objects to a bucket on a bucket page. You can also see options to remove objects, and go back to the previous page.

## References
- https://blog.mandic.com.br/artigos/ceph-armazenamento-em-bloco-do-seculo-xxi/
- https://medium.com/linode-cube/distributed-file-systems-and-object-stores-on-linode-part-2-ceph-41ea514d664e
- https://docs.ceph.com/en/latest/install/
- https://computingforgeeks.com/install-and-configure-ceph-storage-cluster-on-centos-linux/
- https://www.howtoforge.com/tutorial/how-to-build-a-ceph-cluster-on-centos-7/
- https://linuxhint.com/install_centos8_virtualbox/
- https://documentation.suse.com/ses/7/html/ses-all/dashboard-ogw.html
- https://www.howtoforge.com/tutorial/using-ceph-as-block-device-on-centos-7/
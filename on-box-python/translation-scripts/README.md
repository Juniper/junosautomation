# Custom Yang package load with translation script

```
admin@jnpr> request system yang add package p1 module ?
Possible completions:
  <value>              YANG module(s) path
  [                    Open a set of values
  l2vpn.py             Size: 1690, Last changed: Nov 21 18:43:48
  l2vpn.yang           Size: 1484, Last changed: Nov 21 14:57:39
admin@jnpr> request system yang add package p1 module l2vpn.yang translation-script l2vpn.py
YANG modules validation : START
YANG modules validation : SUCCESS
Scripts syntax validation : START
Scripts syntax validation : SUCCESS
TLV generation: START
TLV generation: SUCCESS
Building schema and reloading /config/juniper.conf.gz ...
mgd: commit complete
Restarting mgd ...
 
WARNING: cli has been replaced by an updated version:
Restart cli using the new version ? [yes,no] (yes) yes
 
Restarting cli ...
```

# Custom YANG configuration

```
admin@jnpr> configure
Entering configuration mode

[edit]
admin@jnpr# set l2vpn:l2vpn global as-number 65000
 
[edit]
admin@jnpr# set l2vpn:l2vpn global side hub

[edit]
admin@jnpr# set l2vpn:l2vpn lines line 900 interface ge-0/0/1
 
[edit]
admin@jnpr# set l2vpn:l2vpn lines line 900 vlan 100
 
[edit]
admin@jnpr# set system scripts commit allow-transients
```

# Translated configuration

```
admin@jnpr# show | display translation-scripts translated-config
interfaces {
    ge-0/0/1 {
        description "l2vpn 65000";
        flexible-vlan-tagging;
        encapsulation flexible-ethernet-services;
        unit 0 {
            encapsulation vlan-ccc;
            vlan-id 0;
            family ccc;
        }
    }
}
 
[edit]
admin@jnpr# quit
Exiting configuration mode
```

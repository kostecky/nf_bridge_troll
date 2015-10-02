# nf_bridge_troll
Allow network socket connections to a linux machine if the source_ip has a specific DNS A record for a subdomain that you control. 

This concept dates back to my days administering mail clusters that use DNSBLs to regulate SPAM traffic. This allows you to configure a dynamic firewall with 1 rule that allows you to grant access based on DNS records you control.

![got a red herring?](http://vignette3.wikia.nocookie.net/monkeyisland/images/f/f3/Troll.png)

# Description
Utilizing Linux netfilter's NFQUEUE target we can allow a user space program to make a decision about whether or not a packet is accepted or dropped. We leverage the python bindings for [libnetfilter_queue](https://home.regit.org/netfilter-en/using-nfqueue-and-libnetfilter_queue/) to analyze the source IP of a packet and a DNS A query for `${source_ip}.${acl_domain}` to see if a `127.0.0.2` response is received. If that record exists, it allows the packet through.

## Example

0. A source machine with an IP of 1.2.3.4 connects to a target host that implements this process + NF_QUEUE target in its iptables configuration.

0. The target machine checks to see if the packet is already part of an established connection. If not, it passes it to the NF_QUEUE target.

0. The packet is passed to the callback written in this process, which does the following:
  a. Builds a DNS query based on the source IP: `1.2.3.4.acl.domain.com`
  b. Perform the DNS query
  c. If the RR answer matches `127.0.0.2` the packet is accepted and a connection is established

# Installation and usage
**Warning, this is not without dragons!**

0. You will need to install the development packages on your distro that contain all the requirements that [python-netfilterqueue](https://github.com/kti/python-netfilterqueue) requires.

0. `pip install -r requirements.txt`

0. Use your favourite process manager to launch the `nf_bridge_troll.py` process in the foreground with the `ACL_DOMAIN` environment variable set to the subdomain you control. Something like `acl.yourdomain.com` works well.

0. Ensure that the TTL on your subdomain zone and the records are set low. 1 minute preferably.

0. Insert the last iptables rule below or a variant of it depending on your needs to activate the system. Make sure it comes **after** the RELATED,ESTABLISHED rule that should be a default on most modern distributions.

  ```
  -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
  -A INPUT -p tcp --dport 51235 -j NFQUEUE --queue-num 1
  ```

  This rule will target any tcp packets heading towards port 51235 and send it to queue number 1.

0. Whenever you want to allow a host to have access to a machine, insert an A record in to your ACL_DOMAIN in the following format:

  ```
  123.123.123.123.acl.yourdomain.com.   IN A  127.0.0.2
  ```

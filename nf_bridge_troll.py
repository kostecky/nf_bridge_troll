#!/usr/bin/env python

from netfilterqueue import NetfilterQueue
import dns.query
import dns.resolver
import os
import sys


def query_access(pkt):
    access = False
    pkt_payload = pkt.get_payload()
    # Source IP is located at octet index 12-15 inclusive
    source_ip = '{0}.{1}.{2}.{3}'.format(ord(pkt_payload[12]), ord(pkt_payload[13]), ord(pkt_payload[14]), ord(pkt_payload[15]))
    print pkt, source_ip
    dns_lookup_string = '{0}.{1}'.format(source_ip, acl_domain)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 1
    resolver.lifetime = 1
    try:
        query_answer = resolver.query(dns_lookup_string, 'A')
        for rr in query_answer.rrset:
            if str(rr) == '127.0.0.2':
                print 'Access to {0} granted'.format(source_ip)
                access = True
            else:
                print 'source_ip {0} RR: {1} != 127.0.0.2'.format(source_ip, rr)
    except dns.resolver.NXDOMAIN:
        print 'No such domain {0}'.format(dns_lookup_string)
    except dns.resolver.Timeout:
        print 'Timed out while resolving {0}'.format(dns_lookup_string)
    except dns.exception.DNSException:
        print 'Unhandled exception for {0}'.format(dns_lookup_string)

    if access:
        pkt.accept()
    else:
        print 'Access denied for {0}'.format(source_ip)
        pkt.drop()


def process_packets():
    nfqueue = NetfilterQueue()
    # The first 20 bytes of the IP packet contains the source and destination IP
    nfqueue.bind(1, query_access, range=20)
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        print

if __name__ == '__main__':
    global acl_domain
    acl_domain = os.getenv('ACL_DOMAIN')
    if acl_domain is None:
        sys.exit("Please set the ACL_DOMAIN environment variable")
    process_packets()

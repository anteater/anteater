===============
Virus Total API
===============

API Key
-------

In order to the VirusTotal, you will require an API key. These are free to get
and can be obtained by signing up to the service `here <https://www.virustotal.com/#/join-us>`_. 

Once you have your key, it needs to be set as an environment variable.

If you're using CI, then see each CI document section in these docs for
examples of how to do this.

If either `--ips`, ``--urls`` or ``--bincheck`` are called as arguments (in 
any combination including all three at once), then the VirusTotal API will be
queried for information on the following:

Public IP Addresses
-------------------

If ``--ips`` is used, anteater will perform a scan for public / external IP
Addresses. Once an address is found, the IP is sent to the Virus Total API
and if the IP Address has past assocations with malicous or malware hosting
domains, a failure is registered and a report is provided.


An example report can be seen `here <https://www.virustotal.com/#/ip-address/90.156.201.27>`_.

URLs
----

If ``--urls`` is used, anteater will perform a scan for URL's. If an URL is
found, the URL is sent to the Virus Total API which then compares the URL to
a large list of URL blacklisting services.

An example report can be seen `here <https://www.virustotal.com/#/url/fb69ecad84eb86b1afddcca17aec38daea196e7c883b22ff88a7c39fd8fbdf1a/detection>`_.

Binaries
--------

If ``--bincheck`` is used, anteater will send a hash of the binary to the Virus
Total API which then compares the binary to an aggregation of Virus Scanner
results. If no existing report is available, anteater will send the complete
binary file to Virus Total.

Redis Server
------------

Use of the public Virus Total API requires a rate limit of no more than three
requests per minute. In order to achieve this, we use Redis as means to track
global rate requests and implement a rate limit.

All that is required for the Redis set up, is the installation of Redis and 
running redis with its default values.

The Dockerfile will deploy redis for you. Refer to `installation`_ for more
details.


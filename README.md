# Anteater

![anteater](http://i.imgur.com/BPvV3Gz.png)

Anteater - CI Validation Framework
----------------------------------

Description
-----------

Anteater performs security scanning of any github pull requests or gerrit code
review patches. Each time a patch is pushed to a repository, jenkins
instantiates anteater, who then performs a series of security checks to each
file proposed in a patch.

Checks consist of verification that no binary / blobs are present. If they are,
the build will fail , until a review has occurred to insure the binary is safe
and its origins are known. Once agreed as safe, a sha256 checksum is entered 
into anteaters 'exception' list to insure it is not maliciously replaced at any
given time in the future.

Checks are made to insure the file are not of a sensitive nature, for example
cryptographic keys or application configuration files known to contain
sensitive details, are all blocked from merge.

Finally a deep scan is performed to look for suspect patterns, such as scripts
pulling in file / objects from untrusted sites, or various patterns such as
shell executions.

Anteater uses an open framework to allow users to add new additions easily,
without having to touch any code.

Anteater was developed to address concerns of recent high profile attacks that
have occurred against CI environments, where hackers have backdoor'ed build /
DevOps systems by various means (such as stealing a users ssh key and self
approving patches). By having automated non-human checks in place, it adds an
extra layer of security review with the ability to block a patch merge at gate.

The project is mainly used in the Linux Foundations OPNFV platform, which has
over 40 repositories that need monitoring. This is a fork of that repo with
added ability to run from Travis CI.
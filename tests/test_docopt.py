import unittest
from docopt import docopt
import anteater

from anteater.main import __doc__ as doc


class TestClient(unittest.TestCase):
    def testArgs(self):
        cmd = '--ips --urls --binaries --project test --patchset /home/user/repo/patchset'
        args = docopt(doc, cmd.split(' '))
        self.assertEqual(args['<project>'], 'test')
        self.assertEqual(args['<patchset>'], '/home/user/repo/patchset')


if __name__ == "__main__":
    unittest.main()

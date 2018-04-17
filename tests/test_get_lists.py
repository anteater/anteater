import unittest
from anteater.src import get_lists


class TestClient(unittest.TestCase):
    def testFncs(self):
        project = 'testproject'
        lists = get_lists.GetLists()
        audit_list = lists.file_audit_list(project)
        content_list = lists.file_content_list(project)
        file_ignore = lists.file_ignore()
        ignore_directories = lists.ignore_directories(project)
        url_ignore = lists.url_ignore(project)
        ip_ignore = lists.ip_ignore(project)


if __name__ == "__main__":
    unittest.main()

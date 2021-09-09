try:
    from app import app
    import unittest
except Exception as e:
    print("Some Modules are Missimg: {} ".format(e))

class FlaskTestCase(unittest.TestCase):
    #Check For response code 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/members_json")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if response type is application/json
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/members_json")
        self.assertEqual(response.content_type,'application/json')

    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("/members_json")
        self.assertTrue((b'Name' in response.data) and (b'MIS' in response.data) and (b'Email' in response.data))



if __name__=="__main__":
    unittest.main()

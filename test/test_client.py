from forward_nqe_client import FwdApi
import os

query = '''
{
  devices {
    name
  }
}
'''


def test_query():
    url = os.environ['TEST_DME_SERVER']
    username = os.environ['TEST_DME_SERVER_USERNAME']
    password = os.environ['TEST_DME_SERVER_PASSWORD']
    snapshotId = os.environ['TEST_DME_SNAPSHOT_ID']
    verify = True
    api = FwdApi(url, (username, password), verify)
    dataset = api.query(snapshotId, query)
    assert len(dataset['devices']) == 118

import urllib3
import requests
import json


def runQueryInternal(snapshotId, q, baseUrl, auth, verify):
    url = baseUrl.rstrip("/") + '/api/snapshots/' + str(snapshotId) + '/graphql'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'}
    return requests.post(url, verify=verify, auth=auth, data=json.dumps(q),
                         headers=headers)


def runQuery(snapshotId, query, baseUrl, auth, verify):
    q = {'query': query}
    return runQueryInternal(snapshotId, q, baseUrl, auth, verify)


def runQueryWithVars(snapshotId, query, varsDict, baseUrl, auth, verify):
    q = {'query': query, 'variables': varsDict}
    return runQueryInternal(snapshotId, q, baseUrl, auth, verify)


def formatIpAddr(a):
    addr, prefix = a
    return addr + '/' + str(prefix)


class FwdApi:
    def __init__(self, baseUrl, cred, verify=True):
        self.baseUrl = baseUrl
        self.cred = cred
        self.verify = verify

    def query(self, snapshotId, query):
        result = runQuery(snapshotId, query, self.baseUrl, self.cred,
                          self.verify)
        return result.json()['data']

    def queryWithVars(self, snapshotId, query, varsDict):
        result = runQueryWithVars(snapshotId, query, varsDict, self.baseUrl,
                                  self.cred, self.verify)
        return result.json()['data']


def printTable(header, rows):
    allRows = [header]
    allRows.extend(rows)
    printTableNoHeader(allRows)
    print("%d rows" % len(rows))


def printTableNoHeader(rows):
    # Taken from: https://gist.github.com/lambdalisue/407b706d54619cb32588
    # GistID: 407b706d54619cb32588
    # find the maximum width of each columns
    wcolumns = None
    for columns in rows:
        if not wcolumns:
            wcolumns = [len(str(x)) for x in columns]
        else:
            wcolumns = [max(x, len(str(y))) for x, y in zip(wcolumns, columns)]
    # print columns with the maximum width
    for columns in rows:
        cols = [str(c).ljust(w) for w, c in zip(wcolumns, columns)]
        print("| {} |".format(" | ".join(list(cols))))

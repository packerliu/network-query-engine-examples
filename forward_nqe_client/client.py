import urllib3
import requests
import json
import re


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


def add_cursor(query, pathToPage, cursor):
    wordPattern = re.compile(r'(\w+?)[\(\{]*')
    curIndex = 0
    for match in wordPattern.findIter(query):
        print match.group(1)
        if match == pathToPage[curIndex]:
            curIndex += 1
            if curIndex == len(pathToPage):
                print "Found match at position: " + match.end(0)
                return query[: match.end(0)] + '(from: {})'.format() + query[match.end(0):]

    raise Exception('Could not find path the path in the query: {}'.format(query))


def get_page(dataset, pathToPage):
    page = dataset
    for nextField in pathToPage:
        if not (isinstance(page, list) or isinstance(page, dict)):
            return None
        if nextField not in page:
            return None
        page = page[nextField]
        if isinstance(page, list):
            page = page[0]
    assert 'pageInfo' in page, "Missing the field 'pageInfo' in:\n" + page
    pageInfo = page['pageInfo']
    assert 'hasNextPage' in pageInfo and 'endCursor' in pageInfo, str(pageInfo)
    return page


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

    def iterate_pages(self, snapshotId, query, queryParams, pathToPage):
        result = self.queryWithVars(snapshotId, query, queryParams)
        page = get_page(result, pathToPage)
        if page is None:
            return
        for item in page['items']:
            yield item
        pageInfo = page['pageInfo']
        while pageInfo['hasNextPage']:
            nextPageQuery = add_cursor(query, pathToPage, pageInfo['endCursor'])
            result = self.queryWithVars(snapshotId, nextPageQuery, queryParams)
            page = get_page(result)
            if page is None:
                return
            for item in page['items']:
                yield item


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

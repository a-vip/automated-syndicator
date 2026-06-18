import requests
hashnode_token = "3fa39e25-11b8-4458-adb4-64372b4e92ce"
query = """
query {
  me {
    username
    publications(first: 1) {
      edges {
        node {
          id
        }
      }
    }
  }
}
"""
res = requests.post("https://gql.hashnode.com", json={"query": query}, headers={"Authorization": hashnode_token})
print(res.text)

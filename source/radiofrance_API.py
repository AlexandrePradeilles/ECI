from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://openapi.radiofrance.fr/v1/graphql?x-token=1cd4fb8d-6b32-4140-8e68-385565d381a0")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
{
  diffusionsOfShowByUrl(url: "https://www.franceinter.fr/emissions/en-toute-subjectivite", first: 20) {
	 edges {
      cursor
      node {
          id
          title
          url
          published_date
          podcastEpisode {
            url
            title
          }
      }
    }
  }
}
"""
)

# Execute the query on the transport
result = client.execute(query)


if __name__ == "__main__":
  for i in range(15):
    print(result["diffusionsOfShowByUrl"]["edges"][i]["node"]["podcastEpisode"])
    print("-----------")
  #print(result["diffusionsOfShowByUrl"]["edges"][i]["node"]["podcastEpisode"]['url'])
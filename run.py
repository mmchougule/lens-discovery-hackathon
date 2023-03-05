import streamlit as st
import numpy as np
import pandas as pd
import os

from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from sentence_transformers import SentenceTransformer
from typing import List
import requests


st.set_page_config(layout="wide", page_title="Lens Discovery")

@st.cache_resource
class NeuralSearcher:
    def __init__(self, collection_name: str, cursor=None):
        self.collection_name = collection_name
        self.model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens', device='cpu')
        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant_client = QdrantClient(
            host=os.environ.get("QDRANT_HOST", "b8be5dab-08a0-43ec-ae4a-ed92bbd23805.us-east-1-0.aws.cloud.qdrant.io"),
            api_key=os.environ.get("QDRANT_API_KEY", "Ws4dvr1f4ULm0QUp3Pbvzt4AYaL5Eits6WWi8MbW0fQlub7pP0T6Ew"),
        )

    def search(self, text: str, filter_: dict = None) -> List[dict]:
        vector = self.model.encode(text).tolist()
        payloads = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=Filter(**filter_) if filter_ else None,
            with_payload=True,
            limit=10
        )
        return payloads


n = NeuralSearcher("lens_posts_4")

# Define the GraphQL API endpoint
graphql_url = 'https://api.lens.dev/playground'

@st.cache_resource(ttl=600)
def get_response(query, variables):
    response = requests.post(graphql_url, json={'query': query, 'variables': variables})
    # Parse the response JSON and display the results in Streamlit
    data = response.json()
    return data

query = '''
query {
  explorePublications(
    request: {
      # cursor: "{\"offset\":0}",
      limit: 10,
      publicationTypes: POST,
      sortCriteria: LATEST
    }
  ) {
    items {
      __typename
      ... on Post {
        id
        profile {
          name
          id
        }
        createdAt
        onChainContentURI
        appId
        metadata {
          name
          description
          image
          content
        }
      }
      ... on Comment {
        id
        profile {
          id
          name
        }
        metadata {
          name
          description
          image
          content
        }
        stats {
          id
        }
      }
    }
    pageInfo {
      prev
      next
      totalCount
    }
  }
}
'''
variables = {'genre': 'Science Fiction'}
st.header("Lens Discovery")

def format_text(text):
    results = n.search(text)
    st.header(f"total results found: {len(results)}")
    # row6_spacer1, row6_1, row6_spacer2, row6_2  = st.columns((.2, 4.3, .4, 4.4))
    row6_spacer1, row6_1  = st.columns((.2, 7.3))

    with row6_1:
      for r in results:
        st.write("----------------------------------------------------------------------------------------------------------------------------------------------------")
        st.markdown(
            f'<div style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px; background-color: black">'
            f'<a href="https://lenster.xyz/posts/{r.payload["post_id"]}" style="text-decoration: none; color: #333;">'
            f'<h3>{r.payload["post_id"]}</h3></a><p style="font-size: 14px;">{r.payload["content"]}</p></div>',
            unsafe_allow_html=True
        )


t = st.text_input("Enter text")

if t:
    # st.header("You may also like")
    format_text(t)

# Parse the response JSON and display the results in Streamlit
# data = response.json()
data = get_response(query, variables)


def format_latest(data_raw):
    df = pd.DataFrame(data_raw)
    data = df.drop_duplicates(subset=['id'])
    for r in data.itertuples():
        if r.metadata["content"].strip() == "":
            continue
        # st.write("=====================================")
        st.markdown(#background-color: #270707
            f'<div style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px; ">'
            f'<a href="https://lenster.xyz/posts/{r.id}" style="text-decoration: none; color: #333;">'
            f'<h3>{r.id}</h3></a><p style="font-size: 14px;">{r.metadata["content"]}</p></div>',
            unsafe_allow_html=True
        )

        btn_clicked = st.button(f'More like this: {r.id}')
        if btn_clicked:
            format_text(r.metadata["content"])


st.header("Latest posts")
if data['data']['explorePublications']['items']:
    format_latest(data['data']['explorePublications']['items'])


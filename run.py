import streamlit as st
import numpy as np
import pandas as pd
import os

from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from sentence_transformers import SentenceTransformer
from typing import List
import requests

st.set_page_config(
    page_title="Lens Discovery",
    page_icon=":mag:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Define app colors
background = "#E6F4F1"
primary_color = "#1DBF73"
secondary_color = "#1DA1F2"
text_color = "#262730"

grad1 = "#ee7752"
grad2 = "#e73c7e"
css_style = f"""
    <style>

        .reportview-container, .appview-container.css-1wrcr25.egzxvld6 {{
            background: linear-gradient(to bottom, {grad1} 0%, {grad2} 100%);
        }}
        .css-17eq0hr {{
            color: {text_color};
        }}
        .st-bv.st-bs {{
            padding: 1rem;
            color: {text_color}
        }}
    </style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# Define app layout
header = st.container()
search = st.container()
latest_posts = st.container()
st.header("Lens Discovery")

@st.cache_resource
class NeuralSearcher:
    def __init__(self, collection_name: str, cursor=None):
        self.collection_name = collection_name
        self.model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens', device='cpu')
        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant_client = QdrantClient(
            host=os.environ.get("QDRANT_HOST", "b8be5dab-08a0-43ec-ae4a-ed92bbd23805.us-east-1-0.aws.cloud.qdrant.io"),
            api_key=os.environ.get("QDRANT_API_KEY", ""),
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

# Define GraphQL API endpoint
graphql_url = "https://api.lens.dev/playground"
query = '''
query {
  explorePublications(
    request: {
      # cursor: "{\"offset\":0}",
      limit: 40,
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

@st.cache_resource(ttl=600, show_spinner=False)
def get_response(query, variables):
    response = requests.post(graphql_url, json={"query": query, "variables": variables})
    data = response.json()
    return data

def search_neural(text):
    results = n.search(text)
    return results

def format_text(text):
    results = n.search(text)
    if not results:
        return None
    st.header("posts found")
    row6_spacer1, row6_1  = st.columns((.2, 7.3))

    with row6_1:
      for r in results:
        st.write("----------------------------------------------------------------------------------------------------------------------------------------------------")
        st.markdown(
            f"""
            <a href="https://lenster.xyz/posts/{r.payload["post_id"]}" style="text-decoration: none;" />
            <h3>{r.payload["post_id"]}</h3></a><p style="font-size: 16px;">{r.payload["content"]}</p></div>
            """,
            unsafe_allow_html=True
        )

t = st.text_input("Search for anything...", 
        placeholder="ethdenver hackers",
)
if t:
    st.markdown(
      f"""

      <div class="gradient-background" style="border: 1px solid #ccc; color: #fff, border-radius: 5px; padding: 10px; margin-bottom: 10px; ">
      """,
      unsafe_allow_html=True
    )

    format_text(t)

data = get_response(query, variables)

def format_latest(data_raw):
    df = pd.DataFrame(data_raw)
    data = df.drop_duplicates(subset=['id'])
    for r in data.itertuples():
        if r.metadata["content"].strip() == "":
            continue
        # set the gradient background
        st.markdown(
            f"""

            <div class="gradient-background" style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px; ">
            <a href="https://lenster.xyz/posts/{r.id}" style="text-decoration: none; color: white;">
            <h3>{r.id}</h3></a><p style="font-size: 16px; color: white;">{r.metadata["content"]}</p></div>
            """,
            unsafe_allow_html=True
        )

        btn_clicked = st.button(f'find similar: {r.id}')
        if btn_clicked:
            format_text(r.metadata["content"])
        st.write("----------------------------------------------------------------------------------------------------------------------------------------------------")

st.header("Latest posts")
if data['data']['explorePublications']['items']:
    format_latest(data['data']['explorePublications']['items'])


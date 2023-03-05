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
    layout="wide",
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
            color: {grad2}
        }}
    </style>
"""
st.markdown(css_style, unsafe_allow_html=True)

header_container = st.container()
cols = header_container.columns([1, 3, 1])

with cols[0]:
    st.write("")
with cols[2]:
    st.write("")
with cols[1]:
    st.write("<h1 style='text-align: center;'>Lens Discovery</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>AI-based lens content search and recommendations</p>", unsafe_allow_html=True)

# Define app layout
header = st.container()
search = st.container()
latest_posts = st.container()

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
            limit=15
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

def add_markdown(c, chunk, i):
    with c:
      post_id = chunk[i].payload["post_id"]
      st.markdown(
          f"""
          <div class="gradient-background" style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px; ">
          <a href="https://lenster.xyz/posts/{post_id}" style="text-decoration: none;" />
          <h3>{post_id}</h3></a><p style="font-size: 16px;">{chunk[i].payload["content"]}</p></div>
          """,
          unsafe_allow_html=True
      )

def add_markdown_latest(c, chunk, i):
    with c:
      # st.write(chunk.iloc[i].metadata["content"])

      st.markdown(
          f"""
          <div class="gradient-background" style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px; ">
          <a href="https://lenster.xyz/posts/{chunk.iloc[i].id}" style="text-decoration: none;" />
          <h3>{chunk.iloc[i].id}</h3></a><p style="font-size: 16px;">{chunk.iloc[i].metadata["content"]}</p></div>
          """,
          unsafe_allow_html=True
      )
      btn_clicked = st.button(f'find similar: {chunk.iloc[i].id}')
      if btn_clicked:
          format_text(chunk.iloc[i].metadata["content"])

def format_text(text):
    results = n.search(text)
    if not results:
        return None
    st.header("posts found")
    # row6_spacer1, row6_1  = st.columns((.2, 7.3))
    chunk_size = 3
    for i in range(0, len(results), chunk_size):
        chunk = results[i:i+chunk_size]
        col1, col2, col3 = st.columns(3)

        with col1:
          add_markdown(col1, chunk, 0)
        with col2:
          add_markdown(col2, chunk, 1)
        with col3:
          add_markdown(col3, chunk, 2)

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
    chunk_size = 3
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        col1, col2, col3 = st.columns(3)

        st.write("----------------------------------------------------------------------------------------------------------------------------------------------------")
        with col1:
          add_markdown_latest(col1, chunk, 0)
        with col2:
          add_markdown_latest(col2, chunk, 1)
        with col3:
          add_markdown_latest(col3, chunk, 2)
        st.write("----------------------------------------------------------------------------------------------------------------------------------------------------")

st.write("----------------------------------------------------------------------------------------------------------------------------------------------------")
st.header("Latest posts")
if data['data']['explorePublications']['items']:
    format_latest(data['data']['explorePublications']['items'])


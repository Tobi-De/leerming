from __future__ import annotations

from django.db import models
from model_utils.models import TimeStampedModel
from pgvector.django import VectorField
from django.utils.translation import gettext_lazy as _
from pgvector.django import L2Distance

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TextSplitter,
    Document as LangchainTextDoc,
)
from pathlib import Path
from langchain.embeddings import OpenAIEmbeddings
from django.db.models.query import QuerySet
from leerming.users.models import User
from llama_hub.file.unstructured import UnstructuredReader
from llama_hub.youtube_transcript import YoutubeTranscriptReader
from langchain.document_loaders import UnstructuredURLLoader

import httpx

import stamina


from bs4 import BeautifulSoup


openai_embeddings = OpenAIEmbeddings()


@stamina.retry(on=httpx.HTTPError, attempts=3)
def get_first_title(url: str):
    response = httpx.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    # Find the first available title (h1, h2, h3)
    first_title = (
        soup.find("h1") or soup.find("h2") or soup.find("h3") or soup.find("h4")
    )
    return first_title.text.strip()


class UploadedDocument(TimeStampedModel):
    chunks: QuerySet["DocumentChunk"]

    class DocType(models.TextChoices):
        YOUTUBE_VIDEO = "YOUTUBE_VIDEO", _("Vidéo Youtube")
        TEXT_DOC = "TEXT_DOC", _("Document texte")
        WEB_DOC = "HTML_DOC", _("Page web")

    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="uploaded_documents"
    )
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    doc_type = models.CharField(max_length=255, choices=DocType.choices)

    def __str__(self):
        return self.title

    def get_relevant_chunks_for(self, query: str) -> QuerySet["DocumentChunk"]:
        embedded_query = openai_embeddings.embed_query(query)
        return self.chunks.order_by(L2Distance("embedding", embedded_query))[2]

    @classmethod
    def extract_text_from_doc(cls, filepath: Path) -> list[LangchainTextDoc]:
        loader = UnstructuredReader()
        documents = loader.load_data(file=filepath)
        return [d.to_langchain_format() for d in documents]

    @classmethod
    def extract_text_from_web(cls, url: str) -> list[LangchainTextDoc]:
        loader = UnstructuredURLLoader(
            urls=[url], continue_on_failure=False, headers={"User-Agent": "value"}
        )
        return loader.load()

    @classmethod
    def extract_text_from_youtube(cls, url: str) -> list[LangchainTextDoc]:
        loader = YoutubeTranscriptReader()
        documents = loader.load_data(ytlinks=[url])
        return [d.to_langchain_format() for d in documents]

    @classmethod
    def get_extract_func_for(
        cls, doc_type: DocType
    ) -> callable[[str], list[LangchainTextDoc]]:
        func_to_doc_type = {
            cls.DocType.YOUTUBE_VIDEO: cls.extract_text_from_youtube,
            cls.DocType.TEXT_DOC: cls.extract_text_from_doc,
            cls.DocType.WEB_DOC: cls.extract_text_from_web,
        }
        return func_to_doc_type[doc_type]

    @classmethod
    def get_title_from(cls, obj: str | Path, doc_type: DocType) -> str:
        if doc_type == cls.DocType.TEXT_DOC:
            return Path(obj).stem
        return get_first_title(obj)

    @classmethod
    def get_url_from(cls, obj: str, doc_type: DocType) -> str:
        if doc_type in [cls.DocType.YOUTUBE_VIDEO, cls.DocType.WEB_DOC]:
            return obj
        return ""

    @classmethod
    def get_text_splitter_for(cls, doc_type: DocType) -> TextSplitter:
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        splitter_to_doc_type = {
            cls.DocType.YOUTUBE_VIDEO: recursive_splitter,
            cls.DocType.TEXT_DOC: recursive_splitter,
            cls.DocType.WEB_DOC: recursive_splitter,
        }
        return splitter_to_doc_type[doc_type]

    @classmethod
    def create(cls, obj: str, doc_type: DocType, owner: User) -> None:
        # web probably need it own text splitter
        extract_func = cls.get_extract_func_for(doc_type)
        documents = extract_func(obj)
        text_splitter = cls.get_text_splitter_for(doc_type)

        texts = text_splitter.split_documents(documents)
        vectors = openai_embeddings.embed_documents([t.page_content for t in texts])

        title = cls.get_title_from(obj=obj, doc_type=doc_type)
        url = cls.get_url_from(obj=obj, doc_type=doc_type)
        uploaded_document = cls.objects.create(
            title=title, url=url, doc_type=doc_type, owner=owner
        )

        chunks = []
        for index, vector in enumerate(vectors):
            DocumentChunk(
                document=uploaded_document,
                content=texts[index].page_content,
                embedding=vector,
            )
        DocumentChunk.objects.bulk_create(chunks)


class DocumentChunk(TimeStampedModel):
    document = models.ForeignKey(
        UploadedDocument, on_delete=models.CASCADE, related_name="chunks"
    )
    content = models.TextField()
    embedding = VectorField(dimensions=1536)

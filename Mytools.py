import os

import requests
from langchain.agents import tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient


os.environ["OPENAI_API_BASE"] = os.getenv(
    "DASHSCOPE_API_BASE", ""
)
if os.getenv(""):
    os.environ[""] = os.environ[""]


@tool
def test():
    """Test tool."""
    return "test"


@tool
def searchdx(query: str):
    """仅在需要实时信息或不了解某个概念时使用。"""
    if not os.getenv(""):
        return ""
    return SerpAPIWrapper().run(query)


@tool
def get_info_from_local_db(query: str):
    """仅在回答 2024 年或龙年运势相关问题时使用本地知识库。"""
    db_path = os.getenv("QDRANT_LOCAL_PATH", "ok/local_qdrant")
    client = Qdrant(
        QdrantClient(path=db_path),
        "local_documents",
        OpenAIEmbeddings(model="text-embedding-3-small"),
    )
    return client.as_retriever(search_type="mmr").get_relevant_documents(query)


@tool
def bazi_cesuan(query: str):
    """用于八字排盘；需要用户的姓名及出生年月日时。"""
    api_key = os.getenv("YUANFENJU_API_KEY")
    if not api_key:
        return "尚未配置八字服务密钥。"
    model = ChatOpenAI(model="qwen-plus", temperature=0)
    prompt = ChatPromptTemplate.from_template(
        """根据用户输入提取参数，并且只返回 JSON。字段为 api_key、name、sex、type、year、month、day、hours、minute。
api_key 必须为 {api_key}；sex 中 0 为男、1 为女；type 中 0 为农历、1 为公历，默认 1；minute 默认 0。
若缺少姓名或出生年月日时，返回 {\"error\": \"缺少姓名或出生年月日时\"}。
用户输入：{query}"""
    )
    parser = JsonOutputParser()
    data = (prompt | model | parser).invoke({"query": query, "api_key": api_key})
    if data.get("error"):
        return data["error"]
    response = requests.post("https://api.yuanfenju.com/index.php/v1/Bazi/cesuan", data=data)
    if response.status_code != 200:
        return "技术错误，请稍后再试。"
    try:
        return "八字为：" + response.json()["data"]["bazi_info"]["bazi"]
    except (KeyError, TypeError, ValueError):
        return "八字查询失败，请确认姓名与出生年月日时。"

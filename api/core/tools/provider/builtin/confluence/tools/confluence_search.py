import json
from datetime import datetime
from typing import Any, Union
from urllib.parse import quote
import base64
# import sys
# sys.path.append("/home/cd-dz0105489/dyp/rag/dify_up/api")
import requests
from yarl import URL
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class ConfluenceSearchTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        top_n = tool_parameters.get('top_n', 5)
        query = tool_parameters.get('query', '')

        if not query:
            return self.create_text_message('Please input symbol')
        
  

        # if 'access_tokens' not in self.runtime.credentials or not self.runtime.credentials.get('access_tokens'):
        #     return self.create_text_message("Github API Access Tokens is required.")
        # base_url = "https://wiki.megvii-inc.com"
        base_url = self.runtime.credentials.get('base_url', None)
        username = self.runtime.credentials.get('username', None)
        password = self.runtime.credentials.get('password', None)
        if not base_url:
            return self.create_text_message('Please input base_url')
        if not username:
            return self.create_text_message('Please input company intranet username')
        if not password:
            return self.create_text_message('Please input company intranet password')
        try:
            headers = {
                "Accept": "application/json",
                # "auth":('jiangting', 'Tjhedlen.')
                "Authorization":  f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}",
                # "Authorization": f"Basic {self.runtime.credentials.get('access_tokens')}",
                # "Cookie": "mywork.tab.tasks=false; JSESSIONID=1D324F1E916EFCFE9ED39C52104CEA70; SL_G_WPT_TO=en; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1"
            }
            s = requests.session()
          
            url = str(URL(base_url) / 'rest' / 'api' / 'content' / 'search')
            query_new = {
                'cql': '{{text~"{0}"}}'.format(query),
                #查询语句，text表示查询文本内容，其他标签可以查看官网上的介绍
                #注：这里有一个坑，这儿的匹配不要写=而是要用~ 否则会出现匹配不到结果的情况
                'limit':str(top_n),
                #返回条数
                'expand':"history.contributors",
                #expand包含的是额外的查询结果，history.contributors指的是文档的创始人
                # 'next':next
                #confluence需要通过next来实现下一页的查询功能 因此我们需要提交这个参数
            }
            response = s.request(method='GET', url=url, headers=headers,
                                    params=query_new)
            response_data = response.json()
            if response.status_code == 200:
                contents = list()
                if len(response_data.get('results')) > 0:
                    for item in response_data.get('results'):
                        content = dict()
                        content['story'] = item['_expandable']['space']  #文章所有空间
                        content['type'] = item['type']  #文章类型
                        content['title'] = item['title']  #文章标题
                        content['webui'] =f"{base_url}"+item["_links"]['webui'] #对应的网页链接地址，url需要替换成自己的confluence地址
                        if item['history']['createdBy']['type'] == 'known':
                            content['user'] = item['history']['createdBy']['username']
                        else :
                            content['user'] = "Anonymous"
                        content['updated'] = item['history']['createdDate']
                        contents.append(content)
                    s.close()
                    return self.create_text_message(self.summary(user_id=user_id, content=json.dumps(contents, ensure_ascii=False)))
                else:
                    return self.create_text_message(f'No items related to {query} were found.')
            else:
                return self.create_text_message((response.json()).get('message'))
        except Exception as e:
            return self.create_text_message("Confluence Base url and API token is invalid. {}".format(e))


if __name__=="__main__":
    c = ConfluenceSearchTool()
    res = c._invoke(user_id="123456",  tool_parameters={
                    "query": "蒋霆 HDR",
                    "top_n": 5
                })
    
    print("res:", res)
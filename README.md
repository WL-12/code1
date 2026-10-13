#服务器端:接口-》langchain-》openai\ollama。
#客户端:e。
#接口:http,https,websocket

#服务器: 
1.接口访问，python选型fastapi
2./chat的接口，post请求
3./add_ursl 从url中学习知识
4./add_texts 从txt文本里学习
#人性化
1.用户输入-》AI判断一下当前问题的情绪倾向
2.设计 Agent 自动决策逻辑，支持大模型自主判断并调度外部工具
3.聊天内容精简存入redis构建持久化记忆模块

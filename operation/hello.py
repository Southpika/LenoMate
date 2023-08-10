import operation.fortune as fortune


class bot_hello:
    def __init__(self) -> None:
        self.query_data = '你好，我是LenoMate'

    def hello(self, ast=True):

        if ast:
            "星座运势"
            ast = fortune.query()
            ast_query = ast.constellation()
            if ast_query: self.query_data += '\n您的今日运势为:\n' + ast_query + '请问有什么可以帮您'

        hello = {'chat': self.query_data, 'command': 'START msedge.exe http://localhost:8081/'}
        return hello

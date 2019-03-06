import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.ioloop import IOLoop

from tornado.locks import Semaphore
import tornado.websocket

# from tornado_cors import CorsMixin


import aiohttp  
from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio
import json
import signal  
import sys  
from datetime import datetime
loop = asyncio.get_event_loop()  
client = aiohttp.ClientSession(loop=loop)

subredditTopic = ['futurology', 'explainlikeimfive', 'Nonononoyes' ,'NatureIsFuckingLit','announcements','funny','AskReddit','todayilearned','worldnews']


class MainHandler(tornado.web.RequestHandler):
    async def get(self): 
        # asyncio.ensure_future(use_some_resource('python', client))  
        # asyncio.ensure_future(use_some_resource('programming', client))
        start_time = datetime.now()
        task = await asyncio.ensure_future(runner())
        end_time = datetime.now()
        elapsed = end_time - start_time
        print(elapsed)
        self.write(json.dumps(task))


class EchoWebSocket( tornado.websocket.WebSocketHandler):
    CORS_ORIGIN = '*'
    
    def check_origin(self, origin):
        allow_origin = "*"
        if allow_origin == "*":
            return True

    def open(self):
        print("WebSocket opened")


    async def on_message(self, message):
        print(message)
        params = json.loads(message)
        
        data = await use_some_resource(params['category'], client)
        self.write_message(json.dumps(data))

    def on_close(self):
        print("WebSocket closed")

def signal_handler(signal, frame):  
    loop.stop()
    client.close()
    sys.exit(0)

async def get_json(client, url):  
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()


async def use_some_resource(subreddit, client):
    data1 = await get_json(client, 'https://www.reddit.com/r/' + subreddit + '/top.json?sort=top&t=day&limit=1000')

    j = json.loads(data1.decode('utf-8'))
    posts = []
    
    for i in j['data']['children']:
        post = {}

        post['score'] = i['data']['score']
        post['title'] = i['data']['title']
        post['link'] = i['data']['url']
        post['author'] = i['data']['author']
        post['created'] = i['data']['created_utc']
        
        # print(str(score) + ': ' + title + ' (' + link + ')')
        posts.append(post)
    print('DONE:', subreddit + '\n')
    return {'topic': subreddit, 'posts': posts}

sem = Semaphore(1)

async def worker(worker_id):
    await sem.acquire()
    try:
        print("Worker %d is working" % worker_id)
        posts = await use_some_resource(subredditTopic[worker_id], client)
    finally:
        print("Worker %d is done" % worker_id)
        sem.release()
        return posts        

async def runner():
    # Join all workers.
    return await gen.multi([worker(i) for i in range(subredditTopic.__len__())])


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/socket", EchoWebSocket),
    ])

if __name__ == "__main__":
    app = make_app()
    
    try:
        server = tornado.httpserver.HTTPServer(app)   
        server.bind(1234, '127.0.0.1')
        server.start()
        asyncio.get_event_loop().run_forever().start()
    except KeyboardInterrupt:
        asyncio.get_event_loop().run_forever().stop()
        print("exited cleanly")
   
   


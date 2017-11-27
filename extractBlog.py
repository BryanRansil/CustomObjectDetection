import imghdr
import mimetypes
import os
import pytumblr
import requests
import sys
import urllib

reload(sys)
sys.setdefaultencoding('utf8')

class PhotoNameGenerator(object):
    def __init__(self):
        self.defaultImageNumber = -1
        self.defaultName = 'unnamedImage'

    def __call__(self, post, url):
        response = requests.get(url)
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type)
        name = post.get('slug', self.defaultName)
        print extension
        if (name == self.defaultName or name == '') :
            self.defaultImageNumber += 1
            return self.defaultName + str(self.defaultImageNumber) + extension
        else :
            return name + extension
    

# Authenticate via API Key
client = pytumblr.TumblrRestClient('5tpUWunGLQwglO70dKIURJ6FkYTfs4aPSyFKb01Q4qD4M4LMks')

# Set up global variables
blogName = 'artcive'
blog = blogName + '.tumblr.com'
testfile = urllib.URLopener()
photoNamer = PhotoNameGenerator()
directory = "images/"
if not os.path.exists(directory):
    os.makedirs(directory)

numPosts = client.blog_info(blog).get('blog').get('posts', 0)

for offset in range(0, numPosts, 20) :
    postResponse = client.posts(blog, type='photo', offset=offset)
    if postResponse.get('posts', []) != []:
        postList = postResponse.get('posts', [])
        for post in postList :
            if len(post.get('photos', [])) == 1 and 'pose' in post.get('tags') :
                photoEntry = post.get('photos', [])[0].get('original_size')
                photoName = photoNamer(post, photoEntry.get('url'))
                print photoName
                fullfilename = os.path.join(directory, photoName)
                testfile.retrieve(photoEntry.get('url'), fullfilename)

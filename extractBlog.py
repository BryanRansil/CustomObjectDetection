import pytumblr
import urllib

# Authenticate via API Key
client = pytumblr.TumblrRestClient('5tpUWunGLQwglO70dKIURJ6FkYTfs4aPSyFKb01Q4qD4M4LMks')
blogName = 'artcive'
blog = blogName + '.tumblr.com'

# Make the request
numPosts = client.blog_info(blog).get('blog').get('posts', 0)
numCollectedPosts = 0
print numPosts
for offset in range(0, numPosts, 20) :
    postResponse = client.posts(blog, type='photo', offset=offset)
    if postResponse.get('posts', []) != []:
        postList = postResponse.get('posts', [])
        for post in postList :
            if len(post.get('photos', [])) == 1 and 'pose' in post.get('tags') :
                photoEntry = post.get('photos', [])[0].get('original_size')
                testfile = urllib.URLopener()
                testfile.retrieve(photoEntry.get('url'), post.get('slug', 'default'))


print numCollectedPosts

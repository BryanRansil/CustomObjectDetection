import pytumblr

# Authenticate via API Key
client = pytumblr.TumblrRestClient('5tpUWunGLQwglO70dKIURJ6FkYTfs4aPSyFKb01Q4qD4M4LMks')
blog = 'artcive'

# Make the request
postResponse = client.posts(blog + '.tumblr.com', type='photo')
if postResponse.get('posts', []) != []:
    postList = postResponse.get('posts', [])
    for post in postList :
        if len(post.get('photos', [])) <= 1 and 'pose' in post.get('tags') :
            print "Here!"

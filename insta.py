import urllib2
import urllib
import json
import os

from instagramParams import *

image_resolution = 'thumbnail'  #standard_resolution, low_resolution

hashtag = 'pixelperfectkw'

def ajaxRequest(url=None):
    """
    Makes an ajax get request.
    url - endpoint(string)
    """
    req = urllib2.Request(url)
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    return response    

def pull_images(hashtag, min_tag_id):
    # url to query for pictures
    nextUrl = "https://api.instagram.com/v1/tags/"+hashtag+"/media/recent?access_token="+str(ACCESS_TOKEN)+"&min_tag_id="+str(min_tag_id)

    # While a next URL to go to exists
    while nextUrl:
        
        # Make an instagram request
        instagramJSON = ajaxRequest(nextUrl)
        instagramDict = json.loads(instagramJSON)

        # Attemp to get next URL that matches hashtag
        try:
            min_tag_id = str(instagramDict["pagination"]["next_min_id"])
            print "Min tag"
            print min_tag_id
            nextUrl = instagramDict["pagination"]["next_url"]
            print "Next URL"
            print nextUrl
            
        except:
            nextUrl = None 
            
        instagramData = instagramDict["data"]

        # for every picture
        for picDict in instagramData:
            
            imageUrl = picDict["images"][image_resolution]["url"]
            print str(imageUrl.split('/')[-1])
            
            # Save photo if it doesn't already exist
            if os.path.isfile("./images/" + str(imageUrl.split('/')[-1])) == False: 
                urllib.urlretrieve(imageUrl, "./images/" + str(imageUrl.split('/')[-1]))

    return min_tag_id
    
'''
Main function- maintains display
'''
if __name__ == '__main__':
    min_tag_id = pull_images(hashtag, 0)
    print min_tag_id


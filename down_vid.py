# import urllib2
# import urllib.request as urllib2
# dwn_link = 'http://vidorg.net/embed-t5emyo48ks4r.html'
#
# file_name = 'trial_video.mp4'
# rsp = urllib2.urlopen(dwn_link)
# with open(file_name,'wb') as f:
#     f.write(rsp.read())

import urllib.request
url_link = 'http://vidorg.net/embed-t5emyo48ks4r.html'
video_name = 'Track000000.mp4'
urllib.request.urlretrieve(url_link, video_name)
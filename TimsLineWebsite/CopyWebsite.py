#Program to copy the website to the websites location

#Original location of the website file
orig_location = "TimsLineWebsite.html"
#Destination location of the website file
dest_location = "../../../../var/www/html/TimsLine/TimsLineWebsite.html"

org = open(orig_location, "r")
dest = open(dest_location, "w")
#Write the contents of the original file to the desitination file
dest.write(org.read())
#Close both files
org.close()
dest.close()
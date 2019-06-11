import os

website = True

#Very basic program but it does the job since
print("Resetting the server storage file")
f = open("server_storage.csv", "w")
f.write("Date,DayOfTheWeek,Time,NumberOfPeople,Latitude,Longitude")
f.close
print("Done Reset")

for graph in os.listdir("./Graphs/"):
    print(graph)
    if os.path.isfile("./Graphs/" + graph) and graph != "NoGraph.png":
        os.remove("./Graphs/" + graph)
        print("File Removed!")
        
if website:
    write_graph = open("../../../../var/www/html/TimsLine/server_graph.png", "wb")
    read_graph = open("./Graphs/NoGraph.png", "rb");
    write_graph.write(read_graph.read())
    write_graph.close()
    read_graph.close()
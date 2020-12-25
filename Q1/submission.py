import http.client
import json
import csv


#############################################################################################################################
#
# All instructions, code comments, etc. contained within this notebook are part of the assignment instructions.
# Portions of this file will auto-graded in Gradescope using different sets of parameters / data to ensure that values are not
# hard-coded.
#
# Instructions:  Implement all methods in this file that have a return
# value of 'NotImplemented'. See the documentation within each method for specific details, including
# the expected return value
#
# Helper Functions:
# You are permitted to write additional helper functions/methods or use additional instance variables within
# the `Graph` class or `TMDbAPIUtils` class so long as the originally included methods work as required.
#
# Use:
# The `Graph` class  is used to represent and store the data for the TMDb co-actor network graph.  This class must
# also provide some basic analytics, i.e., number of nodes, edges, and nodes with the highest degree.
#
# The `TMDbAPIUtils` class is used to retrieve Actor/Movie data using themoviedb.org API.  We have provided a few necessary methods
# to test your code w/ the API, e.g.: get_move_detail(), get_movie_cast(), get_movie_credits_for_person().  You may add additional
# methods and instance variables as desired (see Helper Functions).
#
# The data that you retrieve from the TMDb API is used to build your graph using the Graph class.  After you build your graph using the
# TMDb API data, use the Graph class write_edges_file & write_nodes_file methods to produce the separate nodes and edges
# .csv files for use with the Argo-Lite graph visualization tool.
#
# While building the co-actor graph, you will be required to write code to expand the graph by iterating
# through a portion of the graph nodes and finding similar artists using the TMDb API. We will not grade this code directly
# but will grade the resulting graph data in your Argo-Lite graph snapshot.
#
#############################################################################################################################


class Graph:

    # Do not modify
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        """
        option 1:  init as an empty graph and add nodes
        option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0],n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0],e[1]) for e in edges_CSV]


    def add_node(self, id: str, name: str)->None:
        """
        add a tuple (id, name) representing a node to self.nodes if it does not already exist
        The graph should not contain any duplicate nodes
        """

        name = name.encode("ascii", "ignore").decode("ascii", "ignore").replace(',','')

        if (id, name) not in self.nodes:
            self.nodes.append((id, name))
        return 


    def add_edge(self, source: str, target: str)->None:
        """
        Add an edge between two nodes if it does not already exist.
        An edge is represented by a tuple containing two strings: e.g.: ('source', 'target').
        Where 'source' is the id of the source node and 'target' is the id of the target node
        e.g., for two nodes with ids 'a' and 'b' respectively, add the tuple ('a', 'b') to self.edges
        """

        # Check (source, target) does not exist
        if (source, target) not in self.edges and (target, source) not in self.edges:
            # Check source != target
            if source != target:
                self.edges.append((source, target))
        return 


    def total_nodes(self)->int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        return len(self.nodes)


    def total_edges(self)->int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        return len(self.edges)


    def max_degree_nodes(self)->dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}
        """
        degree_set = {}
        max_degree_set = {}
        max_degree = 0

        for i, j in self.edges:
            if i in degree_set:
                degree_set[i] += 1
            else:
                degree_set[i] = 1
            if j in degree_set:
                degree_set[j] += 1
            else:
                degree_set[j] = 1 

        # First, get the max_degree value
        for i, j in degree_set.items():
            if max_degree < j:
                max_degree = j

        # Second, assign the value into max_degree_set
        for i, j in degree_set.items():
            if j == max_degree:
                max_degree_set[i] = j

        return max_degree_set 


    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)


    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)


    # Do not modify
    def write_edges_file(self, path="edges.csv")->None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")



class  TMDBAPIUtils:

    # Do not modify
    def __init__(self, api_key:str):
        self.api_key=api_key


    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list=None) -> list:
        """
        Get the movie cast for a given movie id, with optional parameters to exclude an cast member
        from being returned and/or to limit the number of returned cast members
        documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

        :param integer movie_id: a movie_id
        :param integer limit: number of returned cast members by their 'order' attribute
            e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
            If there are fewer cast members than the specified limit or the limit not specified, return all cast members
        :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
            e.g., if exclude_ids are [353, 455] then exclude these from any result.
        :rtype: list
            return a list of dicts, one dict per cast member with the following structure:
                [{'id': '97909' # the id of the cast member
                'character': 'John Doe' # the name of the character played
                'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ...]
                Note that this is an example of the structure of the list and some of the fields returned by the API. The result of the API call will include many more fields for each cast member.
        Important: the exclude_ids processing should occur prior to limiting output.
        """
        conn = http.client.HTTPSConnection("api.themoviedb.org")
        conn.request("GET", "/3/movie/"+movie_id+"/credits?api_key={}".format(self.api_key)+"&language=en-US")
        res = conn.getresponse()

        # Generate data object
        data = res.read()

        # Convert And parse the data
        parse_data = json.loads(data.decode('utf-8'))

        cast_member = []

        for i in parse_data["cast"]:
            if not limit:
                if exclude_ids:
                    if int(i["id"]) not in exclude_ids:
                        cast_member.append(i)
                else: cast_member.append(i)
            else:
                if int(i["order"]) < limit:
                    if exclude_ids:
                        if int(i["id"]) not in exclude_ids:
                            cast_member.append(i)
                    else: cast_member.append(i)

        return cast_member


    def get_movie_credits_for_person(self, person_id:str, vote_avg_threshold:float=None)->list:
        """
        Using the TMDb API, get the movie credits for a person serving in a cast role
        documentation url: https://developers.themoviedb.org/3/people/get-person-movie-credits

        :param string person_id: the id of a person
        :param vote_avg_threshold: optional parameter to return the movie credit if it is >=
            the specified threshold.
            e.g., if the vote_avg_threshold is 5.0, then only return credits with a vote_avg >= 5.0
        :rtype: list
            return a list of dicts, one dict per movie credit with the following structure:
                [{'id': '97909' # the id of the movie credit
                'title': 'Long, Stock and Two Smoking Barrels' # the title (not original title) of the credit
                'vote_avg': 5.0 # the float value of the vote average value for the credit}, ... ]
        """
        conn = http.client.HTTPSConnection("api.themoviedb.org")
        conn.request("GET", "/3/person/"+person_id+"/movie_credits?api_key={}".format(self.api_key)+"&language=en-US")
        res = conn.getresponse()

        # Generate byte data object
        data = res.read()

        # Convert byte object
        parse_data = json.loads(data.decode('utf-8'))

        movie_credits = []
        
        for i in parse_data["cast"]:
            if i["vote_average"] >= vote_avg_threshold:
                movie_credits.append(i)

        return movie_credits


#############################################################################################################################
#
# BUILDING YOUR GRAPH
#
# Working with the API:  See use of http.request: https://docs.python.org/3/library/http.client.html#examples
#
# Using TMDb's API, build a co-actor network for the actor's/actress' highest rated movies
# In this graph, each node represents an actor
# An edge between any two nodes indicates that the two actors/actresses acted in a movie together
# i.e., they share a movie credit.
# e.g., An edge between Samuel L. Jackson and Robert Downey Jr. indicates that they have acted in one
# or more movies together.
#
# For this assignment, we are interested in a co-actor network of highly rated movies; specifically,
# we only want the top 3 co-actors in each movie credit of an actor having a vote average >= 8.0.
#
# You will need to add extra functions or code to accomplish this.  We will not directly call or explicitly grade your
# algorithm. We will instead measure the correctness of your output by evaluating the data in your argo-lite graph
# snapshot.
#
# Build your co-actor graph on the actress 'Meryl Streep' w/ person_id 5064.
# Initialize a Graph object with a single node representing Meryl Streep
# Find all of Meryl Streep's movie credits that have a vote average >= 8.0
#
# 1. For each movie credit:
#   get the movie cast members having an 'order' value between 0-2 (these are the co-actors)
#   for each movie cast member:
#       using graph.add_node(), add the movie cast member as a node (keep track of all new nodes added to the graph)
#       using graph.add_edge(), add an edge between the Meryl Streep (actress) node
#       and each new node (co-actor/co-actress)
#
#
# Using the nodes added in the first iteration (this excludes the original node of Meryl Streep!)
#
# 2. For each node (actor / actress) added in the previous iteration:
#   get the movie credits for the actor that have a vote average >= 8.0
#   for each movie credit:
#       try to get the 3 movie cast members having an 'order' value between 0-2
#       for each movie cast member:
#           if the node doesn't already exist:
#               add the node to the graph (track all new nodes added to the graph)
#               if the edge does not exist:
#                   add an edge between the node (actor) and the new node (co-actor/co-actress)
#
#
# - Repeat the steps from # 2. until you have iterated 3 times to build an appropriately sized graph.
# - Your graph should not have any duplicate edges or nodes
# - Write out your finished graph as a nodes file and an edges file using
#   graph.write_edges_file()
#   graph.write_nodes_file()
#
# Exception handling and best practices
# - You should use the param 'language=en-US' in all API calls to avoid encoding issues when writing data to file.
# - If the actor name has a comma char ',''"' it should be removed to prevent extra columns from being inserted into the .csv file
# - Some movie_credits may actually be collections and do not return cast data. Handle this situation by skipping these instances.
# - While The TMDb API does not have a rate-limiting scheme in place, consider that making hundreds / thousands of calls
#   can occasionally result in timeout errors. It may be necessary to insert periodic sleeps when you are building your graph.


def return_name()->str:
    """
    Return a string containing your GT Username
    e.g., gburdell3
    Do not return your 9 digit GTId
    """
    return "tliao32"


def return_argo_lite_snapshot()->str:
    """
    Return the shared URL of your published graph in Argo-Lite
    """
    #     small size graph with design of the least edge crossing (15 nodes with the highest degree)
    return "https://poloclub.github.io/argo-graph-lite/#2d36a4d9-3864-4c9d-bfb9-6f4d84996384" 
#     all nodes included (full graph)
#     return "https://poloclub.github.io/argo-graph-lite/#9573f043-8380-4c4d-a73b-11c8b5042110"


if __name__ == "__main__":

    graph = Graph()
    graph.add_node(id='5064', name='Meryl Streep')
    tmdb_api_utils = TMDBAPIUtils(api_key='820073da7ae66a8488fbcb4cfce0b5f3')

    # Set the exclude_ids
    exclude_ids = [5064] 
    cast_member_ids_iter1 = []

    # 1st iteration - Derive cast_members' nodes and edges from Meryl Streep
    for movie_credits in tmdb_api_utils.get_movie_credits_for_person("5064", 8.0):
        # print(movie_credits["id"])
        for cast_member in tmdb_api_utils.get_movie_cast(str(movie_credits["id"]), 3, exclude_ids):
            # add the node for each cast_member
            graph.add_node(str(cast_member["id"]), cast_member["name"])

            # add the edge for each two cast_members
            graph.add_edge("5064", str(cast_member["id"]))

            # add ids for the next iteration
            if cast_member["id"] not in cast_member_ids_iter1:
                cast_member_ids_iter1.append(str(cast_member["id"]))

            # Check if the cast_member is already exist
            if cast_member["id"] not in exclude_ids:
                exclude_ids.append(cast_member["id"]) 

    # 2nd iteration - Derive other cast_members' nodes and edges from the previous cast_members
    cast_members = []
    for i in cast_member_ids_iter1:
        cast_members.append(i)

    cast_member_ids_iter2 = []

    # print(cast_members)
    for id in cast_members:
        # print(id)
        exclude_ids = [int(id)]
        for movie_credits in tmdb_api_utils.get_movie_credits_for_person(id, 8.0):
            for cast_member in tmdb_api_utils.get_movie_cast(str(movie_credits["id"]), 3, exclude_ids):
                # add the node for each cast_member
                graph.add_node(str(cast_member["id"]), cast_member["name"])

                # add the edge for each two cast_members
                graph.add_edge(id, str(cast_member["id"]))

                # add ids for the next iteration
                if cast_member["id"] not in cast_member_ids_iter2:
                    cast_member_ids_iter2.append(str(cast_member["id"]))
                
                # Check if the cast_member is already exist
                if cast_member["id"] not in exclude_ids:
                    exclude_ids.append(cast_member["id"]) 

    # 3rd iteration - Derive other cast_members' nodes and edges from the previous cast_members
    cast_members = []
    for i in cast_member_ids_iter2:
        cast_members.append(i)
        
    # print(cast_members)
    for id in cast_members:
        # print(id)
        exclude_ids = [int(id)]
        for movie_credits in tmdb_api_utils.get_movie_credits_for_person(id, 8.0):
            for cast_member in tmdb_api_utils.get_movie_cast(str(movie_credits["id"]), 3, exclude_ids):
                # add the node for each cast_member
                graph.add_node(str(cast_member["id"]), cast_member["name"])

                # add the edge for each two cast_members
                graph.add_edge(id, str(cast_member["id"]))
                
                # Check if the cast_member is already exist
                if cast_member["id"] not in exclude_ids:
                    exclude_ids.append(cast_member["id"])  

    # call functions or place code here to build graph (graph building code not graded)

    graph.write_edges_file()
    graph.write_nodes_file()
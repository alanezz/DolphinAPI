from django.shortcuts import render
from cassandra.cluster import Cluster
from py2neo import Graph, Node, Relationship
from py2neo import authenticate as auth
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from tokenapi.decorators import token_required

# Create your views here.

@csrf_exempt
def create_new(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                graph_media = Graph()
                auth("localhost:7474", "neo4j", "admin")
                media_query = ('match (n) where n.name = "' +
                            str(request.POST.get('media')) + '" return n')
                media = graph_media.cypher.execute(media_query)
                media_node = media[0][0]

                new_node = Node("New", name = str(request.POST.get('nid')))
                title_node = Node("Title", name = str(request.POST.get('title')))
                date_node = Node("Date", name = str(request.POST.get('date')))
                category_node = Node("Category", name = str(request.POST.get('category')))

                #Neo4j Relationships.
                title_relation = Relationship(new_node, "title", title_node)
                was_created_relation = Relationship(new_node, "was_created", date_node)
                category_relation = Relationship(new_node, "category", category_node)

                media_relation = Relationship(media_node, "has_new", new_node)


                graph_media.create(title_relation)
                graph_media.create(was_created_relation)
                graph_media.create(media_relation)
                graph_media.create(category_relation)

                cluster = Cluster()
                session = cluster.connect('rss')
                session.execute("INSERT INTO news (id, content) VALUES (%s, %s);",
                                (str(request.POST.get('nid')), str(request.POST.get('content'))))

                return  HttpResponse("Ok")
            else:
                return HttpResponse("Your  account is disabled.")
        else:
            return HttpResponse("Falló!")

    else:
        for row in rows:
            response_data[row.id] = row.content
        return JsonResponse(response_data)

@token_required
@csrf_exempt
def get_new(request, new_id):
    graph = Graph()
    cluster = Cluster()
    session = cluster.connect('rss')
    auth("localhost:7474", "neo4j", "admin")
    cypher = graph.cypher
    nid = request.POST.get('nid')
    query = "MATCH (n: New {name: '" + str(new_id) + "'})-[r]->m RETURN n.name, type(r), m.name"
    results = graph.cypher.execute(query)
    response_data = {}
    if len(results) > 0:
        for i in results:
            rows = session.execute("SELECT content FROM news WHERE id = '" + str(i[0])  + "'")
            if len(rows) > 0:
                response_data[str(i[0])] = {str(i[1]): str(i[2]), 'content': rows[0][0]}
    return JsonResponse(response_data)

@csrf_exempt
def get_new_by_media(request, media_id):
    graph = Graph()
    cluster = Cluster()
    session = cluster.connect('rss')
    auth("localhost:7474", "neo4j", "admin")
    cypher = graph.cypher
    nid = request.POST.get('nid')
    query = ("MATCH (n2: Media {name: '" + str(media_id) + "'})-[r2]->n \n" +
            "MATCH n-[r]->m \n" +
            "RETURN n.name, type(r), m.name")
    results = graph.cypher.execute(query)
    response_data = {}
    if len(results) > 0:
        for i in results:
            rows = session.execute("SELECT content FROM news WHERE id = '" + str(i[0])  + "'")
            if len(rows) > 0:
                response_data[str(i[0])] = {str(i[1]): str(i[2]), 'content': rows[0][0]}
    return JsonResponse(response_data)

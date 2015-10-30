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

                new_node = Node("New", name = str(request.POST.get('nid')))
                title_node = Node("Title", name = str(request.POST.get('title')))
                date_node = Node("Date", name = str(request.POST.get('date')))
                category_node = Node("Category", name = str(request.POST.get('category')))

                places = request.POST.getlist('places')
                facts = request.POST.getlist('facts')
                people = request.POST.getlist('people')

                if not places:
                    places = []
                if not facts:
                    facts = []
                if not people:
                    people = []

                places_relations = []
                people_relations = []
                facts_relations = []

                for place in places:
                    place_node = Node("Place", name = place)
                    place_relation = Relationship(new_node, "place", place_node)
                    places_relations.append(place_relation)

                for person in people:
                    person_node = Node("Person", name = person)
                    person_relation = Relationship(new_node, "person", person_node)
                    people_relations.append(person_relation)

                for fact in facts:
                    fact_node = Node("Fact", name = fact)
                    fact_relation = Relationship(new_node, "person", fact_node)
                    facts_relations.append(fact_relation)



                #Neo4j Relationships.
                title_relation = Relationship(new_node, "title", title_node)
                was_created_relation = Relationship(new_node, "was_created", date_node)
                category_relation = Relationship(new_node, "category", category_node)

                graph_media.create(title_relation)
                graph_media.create(was_created_relation)
                graph_media.create(category_relation)

                for place_relation in places_relations:
                    graph_media.create(place_relation)

                for fact_relation in facts_relations:
                    graph_media.create(fact_relation)

                for person_relation in people_relations:
                    graph_media.create(person_relation)

                cluster = Cluster()
                session = cluster.connect('rss')
                session.execute("INSERT INTO news (id, content) VALUES (%s, %s);",
                                (str(request.POST.get('nid')), str(request.POST.get('content'))))

                session.execute("INSERT INTO news_media (id, media, up_date) VALUES (%s, %s, dateof(now()));",
                                (str(request.POST.get('nid')), str(request.POST.get('media'))))

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
    query = "MATCH (n: New {name: '" + str(new_id) + "'})-[r]->m RETURN type(r), m.name"
    results = graph.cypher.execute(query)
    if len(results) > 0:
        rows = session.execute("SELECT content FROM news WHERE id = '" + str(new_id)  + "'")
        aux_dict = {}
        aux_dict['nid'] = str(new_id)
        aux_dict['fact'] = []
        aux_dict['person'] = []
        aux_dict['place'] = []
        if len(rows) > 0:
            aux_dict['content'] = rows[0][0]
        for i in results:
            if (str(i[0]) == 'fact' or
                str(i[0]) == 'place' or
                str(i[0]) == 'person'):
                aux_dict[str(i[0])].append(str(i[1]))
            else:
                aux_dict[str(i[0])] = str(i[1])
    return JsonResponse(aux_dict)

@token_required
@csrf_exempt
def get_new_by_media(request, media_id, limit):
    graph = Graph()
    cluster = Cluster()
    session = cluster.connect('rss')
    response_data = {}
    if int(limit) > 0:
        query = "SELECT id FROM news_media WHERE media = '" + str(media_id)  + "' ORDER BY up_date DESC LIMIT " + str(limit)
        print(query)
        rows = session.execute(query)
    else:
        query = "SELECT id FROM news_media WHERE media = '" + str(media_id)  + "' ORDER BY up_date DESC"
        print(query)
        rows = session.execute(query)
    if len(rows) > 0:
        for i in rows:
            content = session.execute("SELECT content FROM news WHERE id = '" + str(i[0])  + "'")
            if len(content) > 0:
                if len(content[0]) > 0:
                    response_data[str(i[0])] = content[0][0]
    return JsonResponse(response_data)

@token_required
@csrf_exempt
def filter_new(request, place, person, fact):
    graph = Graph()
    cluster = Cluster()
    session = cluster.connect('rss')
    auth("localhost:7474", "neo4j", "admin")
    cypher = graph.cypher
    nid = request.POST.get('nid')
    s = ""
    if len(place) > 0:
        s += "MATCH(n: New)-[r:place]->(m {name: '" + str(place) + "'}) \n"
    if len(person) > 0:
        s += "MATCH(n: New)-[r2:person]->(m2 {name: '" + str(person) + "'}) \n"
    if len(fact) > 0:
        s += "MATCH(n: New)-[r3:fact]->(m3 {name: '" + str(fact) + "'}) \n"
    if len(s) == 0:
        return JsonResponse({})
    else:
        s += "RETURN n.name"
    results = graph.cypher.execute(s)
    aux_dict = {}
    for result in results:
        rows = session.execute("SELECT content FROM news WHERE id = '" + str(result[0])  + "'")
        if len(rows) > 0:
            aux_dict[str(result[0])] = rows[0][0]
    return JsonResponse(aux_dict)

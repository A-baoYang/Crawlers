from wikidata.client import Client
client = Client()  # doctest: +SKIP
entity = client.get('Q463094', load=True)
print(entity.description)

sub_comp = entity[client.get('P355')]
# print(sub_comp.type)  # item
print(len(sub_comp.lists()))

for comp in sub_comp.lists():
    p, ent_list = comp[0], comp[1]
    print(p.description) if type(p) != str else print(p)
    for ent in ent_list:
        print(ent.description) if type(ent) != str else print(ent)


import json


coords = [
    (37.75787124023439, -122.4136349847871),
    (37.75780338199228, -122.41586658268749),
    (37.757396231232505, -122.41809818058788),
    (37.75617476550832, -122.41964313298045),
    (37.75427466763, -122.42024394779979),
    (37.75257811043116, -122.41964313298045),
    (37.751695885313936, -122.41758319645702),
    (37.75122083666311, -122.41483661442577),
    (37.75101724345059, -122.41174670964061),
    (37.75094937892193, -122.40865680485545),
    (37.75101724345059, -122.40651103764354),
    (37.75298528770671, -122.40608188420116),
    (37.75468183556912, -122.4070260217744),
    (37.75631048491801, -122.40831348210155),
    (37.757599806892486, -122.4099442651826),
    (37.75719265501232, -122.41209003239452),
    (37.758414103930434, -122.41372081547557),
    (37.75787124023439, -122.4136349847871),
]


def make_fetch_js(coords):
    polygon = "|".join(f"{lat},{lon}" for lat, lon in coords)

    body = json.dumps({
        "operationName": "SaveCustomRegion",
        "variables": {
            "customRegionToSave": {
                "convertToWkt": True,
                "polygon": polygon,
            }
        },
        "query": (
            "mutation SaveCustomRegion($customRegionToSave: SaveCustomRegionInput!) {\n"
            "  saveCustomRegion(customRegionToSave: $customRegionToSave) {\n"
            "    polygon\n"
            "    customRegionId\n"
            "  }\n"
            "}\n"
        ),
    })

    return f"""fetch('https://www.zillow.com/zg-graph?operationName=SaveCustomRegion', {{
  method: 'POST',
  headers: {{
    'accept': '*/*',
    'content-type': 'application/json',
    'x-caller-id': 'search-page-map'
  }},
  body: {body}
}}).then(r => r.json()).then(console.log).catch(console.error)"""


print(make_fetch_js(coords))

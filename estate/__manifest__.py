
{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base', 'web'],
    'author': "sgeede",
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': 
    [    'security/ir.model.access.csv', 
       'views/estate_menu.xml',    
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tags_views.xml',
        'views/res_users_views.xml'
    ],
    # data files containing optionally loaded demonstration data
    "application" : True,
}
# -*- coding: utf-8 -*-
{
    "name": """Web Widget Image Annotation""",
    "summary": """Web Widget Image Annotation""",
    "category": "web",
    "description": """

            For Form View - added = widget="colorpicker"
            
            ...
            <field name="arch" type="xml">
                <form string="View name">
                    ...
                    <field name="colorpicker" widget="colorpicker"/>
                    ...
                </form>
            </field>
            ...

    """,

    "author": "",

    "depends": [
        "web"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'view/web_widget_image_annotation_view.xml'
    ],
    "qweb": [
        'static/src/xml/widget.xml',

    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
    "application": False,
}

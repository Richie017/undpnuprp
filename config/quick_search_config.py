__author__ = 'ruddra'

QUICK_SEARCH_APP = ('blackwidow.core','blackwidow.sales')
QUICK_SEARCH_PROPERTY={
                    'organization': {
                        'fields' : ['name'],
                        'url' : '/organizations/details/',
                        'title': 'name',
                        'description': 'name'
                        },

                    'role': {
                        'fields': ['name'],
                        'url' : '/roles/details/',
                        'title': 'name',
                        'description': 'name'
                            },

                    'product': {
                        'fields' : ['code','description','flavour'],
                        'url' : '/products/details/',
                        'title': 'code',
                        'description': 'description'
                        },

                    'productgroup': {
                        'fields' : ['name'],
                        'url' : '/product-groups/details/',
                        'title': 'name',
                        'description': 'name'
                        },

                    'zone': {
                        'fields': ['name','code'],
                        'url' : '/zones/details/',
                        'title': 'name',
                        'description': 'code'
                        },

                    'area': {
                        'fields': ['name','code'],
                        'url' : '/areas/details/',
                        'title': 'name',
                        'description': 'code'
                    },


                    'outlet': {
                        'fields': ['name','code'],
                        'url' : '/outlets/details/',
                        'title': 'name',
                        'description': 'code'
                    },


                    'route': {
                        'fields': ['name','code'],
                        'url' : '/routes/details/',
                        'title': 'name',
                        'description': 'code'
                    },


                    'sale': {
                        'fields': ['code','invoice_number', 'distributor_code', 'outlet_code', 'payment_method', 'description'],
                        'url' : '/sale/sales/details/',
                        'title': 'code',
                        'description': 'description'
                    },


                    'salesreturn': {
                        'fields': [ 'sales_code', 'invoice_number', 'grn_note_number', 'outlet_code', 'description','delivery_order'],
                        'url' : '/sale/sales-returns/details/',
                        'title': 'code',
                        'description': 'description'
                    },

                    }
# -*- coding: utf-8 -*-
"""Dashboard routes that lead to JSONs without providing parameters."""
routes = {
    'netwide': {
        'client_list': '/usage/client_list_json',
        'topology': '/l3_topology/show',
        'event_types': '/dashboard/event_autocomplete_types',
        'alerts': '/alerts/show',
        'admin_emails': '/alerts/typeahead_emails',
        'possible_clients': '/alerts/possible_clients',
        'inventory': '/organization/inventory_data',
        'event_log': '/dashboard/event_log#',
        'users': '/configure/guests',
    },
    'node': { 
        'node_info': '/nodes/json?orgwide=true',
        'node_settings': '/configure/settings',
    },
    'mx': {
        'dhcp_subnet': '/nodes/dhcp_subnet_json',
        'router_settings': '/configure/router_settings_json',
        'wireless': '/configure/radio_json',
        'routes': '/nodes/get_routes_json',
        'fetch_networks': '/vpn/fetch_networks',
        'fetch_inter': '/vpn/fetch_inter_usage',
    },
    'ms': {
        'switchports': '/nodes/ports_json',
        'dai': '/configure/switch_heterogeneous_features_json/dai',
        'switch_l3': '/switch_l3/show',
        'ipv6_acl': '/configure/switch_heterogeneous_features_json/ipv6_acl',
        'ipv4_meraki_acl': '/configure/switch_meraki_acl_json',
        'ipv4_user_acl': '/configure/switch_user_acl_json',
        'switch_walled_garden': '/configure/switch_heterogeneous_features_json'
                                '/sm_and_walled_garden',
        'qos': '/configure/switch_heterogeneous_features_json/port_range_qos',
        'firmware_upgrades': '/configure/firmware_upgrades_json',
    },
    'mr': {
        'rf_profiles': '/configure/render_rf_profiles_json',
        'rf_interference': '/configure/interference_json',
        'ssids': '/configure/ssids_json',
        'mr_topology': '/nodes/get_topology',
        'air_marshal_config': '/dashboard/load_air_marshal_config',
        'air_marshal_containment': '/dashboard/load_air_marshal_containment',
        'foreign_ssids': '/dashboard/foreign_ssids',
        'rf_overview': '/nodes/rf_overview_data',
        'wireless_health': '/network_health/data_json',
        'raw_connections': '/network_health/raw_connections_json',
        'rf_profiles_config': '/configure/radio2_json'
    },
    'org': {
        'administered_orgs': '/organization/administered_orgs',
        'FILL ME OUT': 'I am incomplete!'
    },
    'insight': {
        'FILL ME OUT': 'I am incomplete!'
    }
}
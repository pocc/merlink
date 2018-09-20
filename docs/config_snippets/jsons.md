# administered_orgs json blob.
    Location: Everywhere
    
    For orgs that are not being accessed by the browser, node_groups = {}.
    For this reason, the administered_orgs json needs to be retrieved every
    time the user goes to a different organization.
    
    * get_networks should only be called on initial startup or if a
      different organization has been chosen
    * browser should have clicked on an org in the org selection page so we
      can browse relative paths of an org
    
    administered_orgs (dict): A JSON blob provided by /administered_orgs
        that contains useful information about orgs and networks. An eid
        for an org or network is a unique way to refer to it.
    
        = {
            <org#1 org_id>: {
                'name' : <org name>
                'url': <url>,
                'node_groups': {
                    <network#1 eid> : {
                        'n': <name>
                        'has_wired': <bool>
                        ...
                    }
                    <network#2 eid> : {}
                    ...
                }
                ...
            }
            <org#2 org_id>: {}
            ...
        }
 
# User JSON blob
    Location: Network-wide > Users

    JSON looks like so, with base64 secret as key for each user:
    {
        "base64 secret": {
            "secret": "base64 secret",
            "name": "First Last",
            "email": "name@domain.com",
            "created_at": unix_timestamp,
            "is_manage_user": true, # is user administrator
            "authed_networks": [  # client vpn/ssid authed network eid list
                  "abc1234",
                  "xyz5678",
            ]
        },
        "base64 secret": {
            "secret": "base64 secret",
            "name": "First Last",
            "email": "name@domain.com",
            ...
    }

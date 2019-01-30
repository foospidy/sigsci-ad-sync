'''
SigSci AD Sync
A helper script for synchronizing AD group users to SigSci site members.
'''

from __future__ import print_function
import os
import sys
import json
from pyad import adgroup, aduser
from pysigsci import sigsciapi

MAP_FILE = "sigsci-ad-map.json"

if __name__ == '__main__':
    try:
        with open('{}'.format(MAP_FILE)) as f:
            mappings = json.load(f)

        sigsci = sigsciapi.SigSciApi(email=os.environ["SIGSCI_EMAIL"],
                                     api_token=os.environ["SIGSCI_API_TOKEN"])

        print('Syncing {} to {}'.format(mappings['ADDomain'], mappings['SigSciCorp']))

        sigsci.corp = mappings['SigSciCorp']

        for group_map in mappings["GroupMappings"]:
            print('----> Syncing users in AD group {}'.format(group_map['ADGroup']))

            sites = []
            group_users = []

            dc_parts = mappings['ADDomain'].split(".")
            DC = ',DC='.join(dc_parts)
            DC = 'DC={}'.format(DC)

            CN = 'CN={},CN=Users'.format(group_map['ADGroup'])

            # Get group
            group = adgroup.ADGroup.from_dn("{},{}".format(CN, DC))

            # Get users array
            for group_user in group.get_members():
                user = aduser.ADUser.from_cn(group_user.name)
                group_users.append(user.mail)

            # Get site(s) array
            corp_sites = sigsci.get_corp_sites()

            if 'message' in corp_sites:
                print('{}'.format(corp_sites['message']))
                sys.exit()

            for site in corp_sites['data']:
                if '*' in group_map['SigSciSites']:
                    sites.append(site['name'])

                elif site['name'] in group_map['SigSciSites']:
                    sites.append(site['name'])

            # Sync users to site(s)
            ## Add users
            for site in sites:
                print('----> Adding {} users to site {}'.format(group_map['ADGroup'], site))
                for user in group_users:
                    # add user
                    try:
                        invite = False

                        print('--------> Adding {} to {} as {}'.format(user,
                                                                       site,
                                                                       group_map['SigSciRole']))
                        data = {
                            "role": group_map['SigSciRole']
                        }
                        result = sigsci.update_site_member(user, data)

                        if 'Invalid resource' in str(result):
                            raise ValueError('MEMBER_NOT_EXIST')
                    except ValueError as err:
                        if str(err) == 'MEMBER_NOT_EXIST':
                            print('------------> Member {} does not exist.'.format(user))
                            invite = True
                    except Exception as err:
                        if str(err) == '400 Bad Request: ID not found':
                            print('------------> User {} does not exist.'.format(user))
                            invite = True
                    finally:
                        if invite:
                            print('------------> Inviting {} to {} as {}'.format(user,
                                                                                 site,
                                                                                 group_map['SigSciRole']))

                            data = {
                                "role": "corpUser",
                                "memberships": {
                                    "data": [{
                                        "site": {
                                            "name": site
                                        },
                                        "role": group_map['SigSciRole']
                                    }]
                                }
                            }
                            result = sigsci.add_corp_user(user, data)

            ## Remove users
            for site in sites:
                print('----> Removing {} members not in AD group {}'.format(site, group_map['ADGroup']))

                sigsci.site = site
                site_members = sigsci.get_site_members()

                if 'message' in site_members:
                    print('{}'.format(corp_sites['message']))
                    sys.exit()

                for user in site_members['data']:
                    if user['user']['email'] not in group_users:
                        print('--------> Removing {}'.format(user['user']['email']))

    except Exception as err:
        print('{}'.format(err))

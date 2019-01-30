# sigsci-ad-sync

A helper script for synchronizing AD group users to SigSci site members.

**WARNING**: This script has had limited testing. Please do your own testing before running it for large synchirnizations.

## Requirements

- Python 3 on Windows.
- Python dependencies are in requirements.txt, run `pip install -r requirements.txt`.
- Must be run on Windows with a domain user that has read access to domain groups and users.
- AD Users must have the email attribute set.
- Signal Sciences API token for a user with Corp Owner permissions.

## Usage

### Authentication for Signal Sciences API

Set the following environment variables (powershell example):

```powershell
> $env:SIGSCI_EMAIL = "your email"
> $env:SIGSCI_API_TOKEN = "your api token"
```

### Configure Mapping

Users and roles are synchronized based on the AD Group to SigSci site and SigSci role mappings defined in `sigsci-ad-map.json`.

#### SigSci Corp and Domain

Edit the first section of the `sigsci-ad-map.json` file to set your corp name and AD domain:

```
{
    "SigSciCorp": "corp_short_name",
    "ADDomain": "corp.foo.com",
    "GroupMappings": [
        ...
    ]
}
```

#### AD Group to SigSci Site Mappings

The next section is the GroupMappings array, add an element to the array for each ADGroup to SigSciSites with the corosponding SigSciRole. For example, if you
want to synchronize all users in the AD Group "SigSci User WebDev" to the site "WebDev" with the role of "User" the GroupMappings section would be:

```json
"GroupMappings": [
    {
        "ADGroup": "SigSci User WebDev",
        "SigSciSites": ["WebDev"],
        "SigSciRole": "user"
    }
]
```

If you also want to synchronize users in the AD Group "SigSci User WebDev" to the site "WebProd" with the role of "observer the GroupMappings section would be:

```json
"GroupMappings": [
    {
        "ADGroup": "SigSci User WebDev",
        "SigSciSites": ["WebDev"],
        "SigSciRole": "user"
    },
    {
        "ADGroup": "SigSci User WebDev",
        "SigSciSites": ["WebProd"],
        "SigSciRole": "observer"
    }
]
```

Note the SigSciSites field is an array. This means you can specify multiple sites. For example, if you want to sync all users in AD group "SigSci Observers" to sites "Site1", "Site2", and "Site3". Example:

```json
"GroupMappings": [
    {
        "ADGroup": "SigSci Observers",
        "SigSciSites": ["Site1", "Site2", "Site3"],
        "SigSciRole": "observer"
    }
]
```

You may also use the wild card `*` to add users of an AD Group to all sites with the specified role. Example:

```json
"GroupMappings": [
    {
        "ADGroup": "SigSci Observers",
        "SigSciSites": ["*"],
        "SigSciRole": "observer"
    }
]
```

### Run the script

`> python sigsciad.py`

Example output:

```powershell
Syncing corp.foo.com to my_corp
----> Syncing users in AD group SigSci Observer All
----> Adding SigSci Observer All users to site site1
--------> Adding user1@mycorp.com to site1 as observer
------------> Member user1@mycorp.com does not exist.
------------> Inviting user1@mycorp.com to site1 as observer
----> Adding SigSci Observer All users to site blamo
--------> Adding user1@mycorp.com to blamo as observer
------------> Member user1@mycorp.com does not exist.
------------> Inviting user1@mycorp.com to blamo as observer
----> Adding SigSci Observer All users to site site2
--------> Adding user1@mycorp.com to site2 as observer
------------> Member user1@mycorp.com does not exist.
------------> Inviting user1@mycorp.com to site2 as observer
----> Adding SigSci Observer All users to site site3
--------> Adding user1@mycorp.com to site3 as observer
------------> Member user1@mycorp.com does not exist.
------------> Inviting user1@mycorp.com to site3 as observer
----> Adding SigSci Observer All users to site site4
--------> Adding user1@mycorp.com to site4 as observer
------------> Member user1@mycorp.com does not exist.
------------> Inviting user1@mycorp.com to site4 as observer
----> Removing site1 members not in AD group SigSci Observer All
--------> Removing user4@mycorp.com
--------> Removing user3@mycorp.com
----> Removing blamo members not in AD group SigSci Observer All
--------> Removing user2@mycorp.com
--------> Removing user4@mycorp.com
--------> Removing user3@mycorp.com
----> Removing site2 members not in AD group SigSci Observer All
--------> Removing user2@mycorp.com
--------> Removing user4@mycorp.com
--------> Removing user3@mycorp.com
----> Removing site3 members not in AD group SigSci Observer All
--------> Removing user4@mycorp.com
--------> Removing user3@mycorp.com
----> Removing site4 members not in AD group SigSci Observer All
--------> Removing user4@mycorp.com
--------> Removing user3@mycorp.com
----> Syncing users in AD group SigSci User Blamo
----> Adding SigSci User Blamo users to site blamo
--------> Adding user1@mycorp.com to blamo as user
----> Removing blamo members not in AD group SigSci User Blamo
--------> Removing user2@mycorp.com
--------> Removing user4@mycorp.com
--------> Removing user3@mycorp.com
```

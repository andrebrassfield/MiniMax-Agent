#!/bin/bash
# Mavis pre-flight check for Dose of Proof LinkedIn Company Page
# Run this after Dre creates the Company Page in LinkedIn + connects it to Buffer
# Author: Mavis (M3 fleet) | Run target: post-Company-Page-creation
#
# v2 (2026-06-25): Buffer GraphQL schema migrated.
#   - channels query now requires `input: { organizationId: ... }`
#   - serviceUsername + description fields removed from Channel type
#   - Use `name`, `displayName`, `serviceId` (urn:li:...) instead
#   - Endpoint: api.buffer.com (the migration in Decision 26)

set -e

ORG_ID="69de6c292b24d8cddc01c3cb"
API_KEY="8vPQVcXSVw3D_TG9S33r-jYhRHZAULCLV9C9xkWG9q8"

echo "================================================================"
echo "LinkedIn Company Page — Buffer Channel Discovery v2"
echo "================================================================"
echo ""
echo "Pre-conditions:"
echo "  1. Dre created Dose of Proof LinkedIn Company Page (10-20 min)"
echo "  2. Dre connected the Company Page to Buffer via OAuth"
echo "  3. Buffer has refreshed its channel list"
echo ""
echo "This script queries Buffer to find the new Company Page channel ID."
echo ""

# Buffer GraphQL query — current schema (2026-06-25)
curl -s -X POST "https://api.buffer.com/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "{\"query\":\"{ channels(input: {organizationId: \\\"${ORG_ID}\\\"}) { id name service serviceId type displayName avatar externalLink isDisconnected } }\"}" \
  | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f'ERROR: invalid JSON response: {e}')
    sys.exit(1)

if 'errors' in data:
    print('API ERRORS:')
    for e in data['errors']:
        print(f'  - {e.get(\"message\", e)}')
    sys.exit(1)

channels = data.get('data', {}).get('channels', [])
print('ALL BUFFER CHANNELS:')
print('-' * 80)
for ch in channels:
    service = ch.get('service', '?')
    name = ch.get('name', '?')
    service_id = ch.get('serviceId', '?')
    cid = ch.get('id', '?')
    ctype = ch.get('type', '?')
    disconnected = ch.get('isDisconnected', False)
    print(f'  Service: {service:10s}  ID: {cid}  Name: {name}  Type: {ctype}  ServiceID: {service_id}  Disconnected: {disconnected}')

print()
print('-' * 80)
print()
print('LINKEDIN CHANNELS:')
for ch in channels:
    if ch.get('service') == 'linkedin':
        cid = ch.get('id', '?')
        name = ch.get('name', '?')
        display_name = ch.get('displayName', '?')
        service_id = ch.get('serviceId', '?')
        ctype = ch.get('type', '?')
        is_personal = ctype == 'profile'
        flag = '[PERSONAL - DO NOT USE]' if is_personal else '[COMPANY PAGE - USE THIS]'
        print(f'  {flag}')
        print(f'     ID: {cid}')
        print(f'     Name: {name}')
        print(f'     Display Name: {display_name}')
        print(f'     Type: {ctype}')
        print(f'     Service ID (LinkedIn URN): {service_id}')
        print()
"
echo ""
echo "================================================================"
echo "NEXT STEPS:"
echo "================================================================"
echo ""
echo "1. Find the [COMPANY PAGE - USE THIS] line above"
echo "2. Copy the ID (looks like: 6a3c4a245ab6d2f1066ad8be)"
echo "3. Send that ID to Mavis — I will:"
echo "   - Update /tmp/buffer_bulk_push.py with the new channel ID"
echo "   - Re-queue LinkedIn Post 1 (Origin Story) for Company Page"
echo "   - Re-queue LinkedIn Carousel 1 (5 Biomarkers) for Company Page"
echo "   - Run the push script with the new channel"
echo ""
echo "4. Mavis will verify both posts are scheduled on Company Page (not personal)"
echo ""
echo "Also needed: delete old personal LinkedIn carousel entries in Buffer UI"
echo "  - Open Buffer UI"
echo "  - Find the carousel entries on personal LinkedIn channel (id: 6a3c1e195ab6d2f10669e738)"
echo "  - Delete the duplicate draft AND the scheduled copy from the earlier pre-rate-limit push run"
echo "  - The active carousel is now on the Company Page channel"
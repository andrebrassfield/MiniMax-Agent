#!/bin/bash
# Mavis pre-flight check for Dose of Proof LinkedIn Company Page
# Run this after Dre creates the Company Page in LinkedIn + connects it to Buffer
# Author: Mavis (M3 fleet) | Run target: post-Company-Page-creation

echo "================================================================"
echo "LinkedIn Company Page — Buffer Channel Discovery"
echo "================================================================"
echo ""
echo "Pre-conditions:"
echo "  1. Dre created Dose of Proof LinkedIn Company Page (10-20 min)"
echo "  2. Dre connected the Company Page to Buffer via OAuth"
echo "  3. Buffer has refreshed its channel list"
echo ""
echo "This script queries Buffer to find the new Company Page channel ID."
echo ""

# Buffer GraphQL query
# NOTE: Buffer migrated from api.bufferapp.com to api.buffer.com
# Use api.buffer.com (new) — old endpoint returns 404
curl -s -X POST "https://api.buffer.com/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 8vPQVcXSVw3D_TG9S33r-jYhRHZAULCLV9C9xkWG9q8" \
  -d '{"query":"{ channels { id service serviceUsername name description avatar organizationId } }"}' \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
channels = data.get('data', {}).get('channels', [])
print('ALL BUFFER CHANNELS:')
print('-' * 80)
for ch in channels:
    service = ch.get('service', '?')
    name = ch.get('name', '?')
    username = ch.get('serviceUsername', '?')
    cid = ch.get('id', '?')
    print(f'  Service: {service:10s}  ID: {cid}  Name: {name}  Handle: {username}')

print()
print('-' * 80)
print()
print('LINKEDIN CHANNELS:')
for ch in channels:
    if ch.get('service') == 'linkedin':
        cid = ch.get('id', '?')
        name = ch.get('name', '?')
        username = ch.get('serviceUsername', '?')
        is_personal = 'personal' in name.lower() or 'andré' in name.lower() or 'dre' in name.lower()
        flag = '[PERSONAL - DO NOT USE]' if is_personal else '[COMPANY PAGE - USE THIS]'
        print(f'  {flag}')
        print(f'     ID: {cid}')
        print(f'     Name: {name}')
        print(f'     Handle: {username}')
        print()
"
echo ""
echo "================================================================"
echo "NEXT STEPS:"
echo "================================================================"
echo ""
echo "1. Find the [COMPANY PAGE - USE THIS] line above"
echo "2. Copy the ID (looks like: 6a3c1e195ab6d2f10669e738)"
echo "3. Send that ID to Mavis — I will:"
echo "   - Update /tmp/buffer_bulk_push.py with the new channel ID"
echo "   - Re-queue LinkedIn Post 1 (Origin Story) for Company Page"
echo "   - Re-queue LinkedIn Carousel 1 (5 Biomarkers) for Company Page"
echo "   - Run the push script with the new channel"
echo ""
echo "4. Mavis will verify both posts are scheduled on Company Page (not personal)"
echo ""
echo "Also needed: delete the Jul 1 LinkedIn carousel from personal LinkedIn"
echo "  - Open Buffer UI"
echo "  - Find the post in personal LinkedIn channel (id: 6a3c1e195ab6d2f10669e738)"
echo "  - Delete it"
echo "  - This was an accident during API exploration; the new Company Page will"
echo "    receive the proper scheduled version"

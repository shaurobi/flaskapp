import requests
import json
from webexteamssdk import WebexTeamsAPI, ApiError
from datetime import datetime, timedelta
import pprint as pp

class Webex:

    def get_oauth_tokens(clientID, secretID, code, redirectURI):
        """Gets access token and refresh token"""
        url = "https://api.ciscospark.com/v1/access_token"
        headers = {'accept':'application/json','content-type':'application/x-www-form-urlencoded'}
        payload = ("grant_type=authorization_code&client_id={0}&client_secret={1}&"
                        "code={2}&redirect_uri={3}").format(clientID, secretID, code, redirectURI)
        try:
            req = requests.post(url=url, data=payload, headers=headers)
            results = json.loads(req.text)
            access_token = results["access_token"]
            expires_in = results["expires_in"]
            refresh_token = results["refresh_token"]
            refresh_token_expires_in = results["refresh_token_expires_in"]
            result = "Success"
        except ApiError as error:
            print (error)
            result = "There was a problem getting the tokens."
        return result, access_token, expires_in, refresh_token, refresh_token_expires_in

    def get_user_info(user_token):
        api = WebexTeamsAPI(access_token=user_token) 
        user = api.people.me()
        pp.pprint(user)
        """Retreives OAuth user's details."""
        personID = user.id
        emailID = user.emails[0]
        displayName = user.displayName
        status = user.status
        try:
            avatar = user.avatar
            print ("avatar: " + avatar)
        except:
            print ("no avatar")
            avatar = ""
        return personID, emailID, displayName, status, avatar

    def get_user(personId, user_token):
        api = WebexTeamsAPI(access_token=user_token) 
        user = api.people.get(personId)
        return user

    def get_rooms(user_token, person_ID, room_filter):
        api = WebexTeamsAPI(access_token=user_token) 
        rooms = api.rooms.list(type='group', sortBy='created')
        if room_filter == "creator":
            room_list = [(room.id,room.title) for room in rooms if room.creatorId == person_ID]
        else:
            room_list = [(room.id,room.title) for room in rooms]
        return room_list

    def get_members(user_token, roomId):
        api = WebexTeamsAPI(access_token=user_token) 
        members = api.memberships.list(roomId=roomId)
        me = api.people.me()
        Member_List = []
        for member in members:
            if "@webex.bot" not in member.personEmail and "@sparkbot.io" not in member.personEmail and member.personId != me.id:
                values = {}
                values['email'] = member.personEmail
                values['displayName'] = member.personDisplayName
                values['coHost'] = False
                Member_List.append(values)
        print (Member_List)
        return Member_List

    def add_users(user_token, email, personID, spaceId):
        api = WebexTeamsAPI(access_token=user_token)
        try:
            if personID == "":
                api.memberships.create(roomId=spaceId, personEmail=email)
                result = "Success"
            else:
                api.memberships.create(roomId=spaceId, personId=personID)
                result = "Success"
        except ApiError as error:
            try:
                api.rooms.get(roomId=spaceId)
                memberships = api.memberships.list(roomId=spaceId)
                for membership in memberships:
                    if personID == "":
                        if membership.personEmail == email:
                            result = "User already exists in space"
                            break
                        elif membership.personId == personID:
                            result = "User already exists in space"
                            break
                    else:
                        result = "Error: There was a problem addding this user."
            except ApiError as error:
                result = "Error: There was a problem adding users to this space."
        return result

    def create_space(user_token, spaceName):
        api = WebexTeamsAPI(access_token=user_token)
        try:
            room = api.rooms.create(title=spaceName)
            roomId=room.id
            result = "Success"
        except ApiError as error:
            result = "There was a problem creating the space."
        return result, roomId

    def delete_space(user_token, roomId):
        api = WebexTeamsAPI(access_token=user_token)
        try:
            room = api.rooms.delete(roomId)
            result = "Deleted"
        except ApiError as error:
            result = "There was a problem deleting the space."
        return result

    def get_refresh_token(clientID, secretID, refresh_token):
        api = WebexTeamsAPI()
        try:
            refresh = api.access_tokens.refresh(client_id=clientID, client_secret=secretID, refresh_token=refresh_token)
            access_token = refresh.access_token
            expires_in = refresh.expires_in
            new_refresh_token = refresh.refresh_token
            refresh_token_expires_in = refresh.refresh_token_expires_in
            result = "Success"
        except ApiError as error:
            print (error)
            result = "There was a problem refreshing the token."
            print (result)
        return result, access_token, expires_in, new_refresh_token, refresh_token_expires_in

    def send_message(user_token, spaceId, message, markdown):
        api = WebexTeamsAPI(access_token=user_token)
        try:
            if markdown == '':
                sendmsg = api.messages.create(roomId=spaceId,text=message)
            else:
                sendmsg = api.messages.create(roomId=spaceId,markdown=markdown)
            result = "Success"
        except ApiError as error:
            result = "There was a problem sending the message."
        return result

    def create_webhook(user_token, webhookURI, webhookID):
        api = WebexTeamsAPI(access_token=user_token)
        if webhookID is None:
            try:
                webhook = api.webhooks.create(name="OOO-Assistant Webhook",targetUrl=webhookURI,resource="messages", event="created")
                webhookID = webhook.id
                print(webhookID)
                result = "Success"
            except ApiError as error:
                result = "There was a problem creating the webhook."
        else:
            try:
                get_webhook = api.webhooks.get(webhookID)
                print ("Webhook is " + get_webhook.status)
                result = "Success"
            except ApiError as error:
                print ("There was a problem getting the webhook, it was probably deleted.")
                try:
                    webhook = api.webhooks.create(name="OOO-Assistant Webhook",targetUrl=webhookURI,resource="messages", event="created")
                    webhookID = webhook.id
                    print(webhookID)
                    result = "Success"
                except ApiError as error:
                    result = "There was a problem creating the webhook."
        return result, webhookID

    def send_directmessage(user_token, personID, message, markdown):
        if user_token == '':
            user_token = BOT_Token
        api = WebexTeamsAPI(access_token=user_token)
        try:
            if markdown == '':
                sendmsg = api.messages.create(toPersonId=personID, text=message)
            else:
                sendmsg = api.messages.create(toPersonId=personID, markdown=markdown)
            result = "Success"
        except ApiError as error:
            print (error)
            result = "There was a problem sending the message."
        return result

    def get_message(user_token, messageId):
        if user_token == '':
            user_token = BOT_Token
        api = WebexTeamsAPI(access_token=user_token)
        try:
            message = api.messages.get(messageId)
            result = "Success"
        except ApiError as error:
            print (error)
            result = "There was a problem sending the message."
            message = {}
        return result, message

    def get_messages(user_token, spaceID, personID):
        api = WebexTeamsAPI(access_token=user_token)
        try:
            msgs = api.messages.list(roomId=spaceID,max=50)
            msg_list = [(msg.id,msg.text) for msg in msgs if msg.personId == personID]
            result = "Success"
        except ApiError as error:
            result = "There was a problem sending the message."
        return result, msg_list

    def delete_message(user_token, msgID):
        if user_token == '':
            user_token = BOT_Token
        api = WebexTeamsAPI(access_token=user_token)
        try:
            msgs = api.messages.delete(msgID)
            result = "Message deleted"
        except ApiError as error:
            print ("error: " + str(error))
            result = "There was a problem deleting the message."
        return result

    def get_guest_token(jwt_token):
        print ('jwt token = ' + jwt_token)
        url = "https://api.ciscospark.com/v1/jwt/login"
        headers = {'accept':'application/json','Content-Type':'application/json','Authorization': 'Bearer '+ jwt_token}
        req = requests.post(url=url, headers=headers)
        results = json.loads(req.text)
        print (results)
        token = results["token"]
        print (token)
        return token

    def get_attachment(data_id):
        url = "https://api.ciscospark.com/v1/attachment/actions/%s" % data_id
        headers = {
            'Authorization': "Bearer %s" % BOT_Token,
            'Content-Type': "application/json"
            }
        response = requests.get(url, headers=headers)
        json_data = json.loads(response.text)
        return json_data

    def create_meeting(Title, StartTime, EndTime, access_token, pwd, Record, Invite_Members, roomId, TZ):
        url = "https://api.ciscospark.com/v1/meetings"
        payload = {
            "title": Title,
            "password": pwd,
            "start": StartTime,
            "end": EndTime,
            "timezone": TZ
            }
        if Invite_Members == "true":
            Member_List = Webex.get_members(access_token, roomId)
            payload.update( {"invitees": Member_List} )
        if Record:
            payload.update( {"enabledAutoRecordMeeting": Record} )
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        pp.pprint(payload)
        response = requests.post(url, headers=headers, json=payload)
        print ("Response Code: " + str(response.status_code))
        results = {}
        if response.status_code == 200:
            try:
                results = json.loads(response.text)
                success = True
            except Exception as e:
                print ("Error: " + str(e))
                success = False
        else:
            success = False
        return success, results

    def get_calls(CallStatus, access_token):
        url = "https://api.ciscospark.com/v1/calls?status=" + CallStatus
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        response = requests.get(url, headers=headers)
        results = json.loads(response.text)
        Call_List = []
        try:
            for call in results['items']:
                if call['type'] == "meeting":
                    values = {}
                    values['CallId'] = call['id']
                    values['MeetingId'] = call['meetingId']
                    values['duration'] = call['duration']
                    Call_List.append(values)
        except Exception as e:
            print ("Error: " + str(e))
        return Call_List

    def get_call_memberships(CallId, access_token):
        url = "https://api.ciscospark.com/v1/call/memberships?callStatus=connected&callId=" + CallId
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        response = requests.get(url, headers=headers)
        results = json.loads(response.text)
        Members_List = []
        try:
            for member in results['items']:
                values = {}
                values['personId'] = member['personId']
                user = Webex.get_user(member['personId'], access_token)
                values['displayName'] = user.displayName
                values['isHost'] = member['isHost']
                values['status'] = member['status']
                values['joinedDuration'] = member['joinedDuration']
                Members_List.append(values)
        except Exception as e:
            print (e)
        return Members_List

    def get_meeting(MeetingNumber, access_token):
        print ("getting meeting id: " + MeetingNumber)
        url = "https://api.ciscospark.com/v1/meetings?meetingNumber=" + MeetingNumber
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        response = requests.get(url, headers=headers)
        Meeting = {}
        try:
            results = json.loads(response.text)
            Meeting['title'] = results['items'][0]['title']
            Meeting['StartTime'] = results['items'][0]['start']
            Meeting['HostUserId'] = results['items'][0]['hostUserId']
            Meeting['Host'] = results['items'][0]['hostDisplayName']
            Meeting['SIP_Address'] = results['items'][0]['sipAddress']
            Meeting['Web_Link'] = results['items'][0]['webLink']
            result = "success"
        except Exception as e:
            result = "Response Code: " + str(response.status_code)
            print (result)
            print ("Error: " + str(e))
        try:
            Meeting['Host_Key'] = results['items'][0]['hostKey']
            Meeting['password'] = results['items'][0]['password']
        except Exception as e:
            print ("Error: " + str(e))
        return Meeting, result

    def get_meetings(MeetingType, access_token, offset):
        print ("getting scheduled meetings")
        url = "https://api.ciscospark.com/v1/meetings?meetingType=" + MeetingType
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        response = requests.get(url, headers=headers)
        MeetingsList = []
        try:
            results = json.loads(response.text)
            for mtg in results['items']:
                Meeting = {}
                Meeting['title'] = mtg['title']
                meetingnumber = mtg['meetingNumber']
                MeetingId = meetingnumber[0:3] + " " + meetingnumber[3:6] + " " + meetingnumber[6:9]
                Meeting['meetingNumber'] = MeetingId
                datetime_object = datetime.strptime(mtg['start'], '%Y-%m-%dT%H:%M:%SZ')
                StartTime = datetime_object - timedelta(minutes=int(offset))
                Meeting['StartTime'] = StartTime
                Meeting['HostUserId'] = mtg['hostUserId']
                Meeting['Host'] = mtg['hostDisplayName']
                Meeting['SIP_Address'] = mtg['sipAddress']
                Meeting['Web_Link'] = mtg['webLink']
                Meeting['Host_Key'] = mtg['hostKey']
                Meeting['password'] = mtg['password']
                Meeting['callInNumbers'] = mtg['telephony']['callInNumbers']
                MeetingsList.append(Meeting)
            result = "success"
        except Exception as e:
            result = "Response Code: " + str(response.status_code)
            print ("Error: " + str(e))
        return MeetingsList, result

    def get_recording(access_token):
        url = "https://api.ciscospark.com/v1/recordings?max=1"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        response = requests.request("GET", url, headers=headers)
        results = json.loads(response.text)
        pp.pprint(results)
        try:
            playbackUrl = results['items'][0]['playbackUrl']
            password = results['items'][0]['password']
        except Exception as e:
            print ("get_recording error: " + str(e))
            playbackUrl is None
            password is None
        return playbackUrl, password

    def get_sites(access_token):
        url = "https://api.ciscospark.com/v1/meetingPreferences/sites"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
        }
        response = requests.request("GET", url, headers=headers)
        defaultSite = ""
        sites = []
        try:
            results = json.loads(response.text)
            pp.pprint(results)
            sites = results['sites']
            for site in sites:
                if site['default']:
                    defaultSite = site['siteUrl']
                    print ("default site: " + defaultSite)
        except Exception as e:
            print ("get_sites error: " + str(e))
        return defaultSite, sites